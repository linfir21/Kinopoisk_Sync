import asyncio
from playwright.async_api import async_playwright
import db
from config import USERS


async def parse_all():
    db.init_db()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )

        for user_id, user_data in USERS.items():
            if not user_data["kp_id"]:
                continue

            print(f"Парсинг {user_data['name']}...")
            page = await context.new_page()

            await parse_section(page, user_id, user_data["kp_id"], "movies/voted-watched", "watched")

            print("  Пауза 5 секунд...")
            await page.wait_for_timeout(5000)

            await parse_section(page, user_id, user_data["kp_id"], "movies/planned-to-watch", "watchlist")

            await page.close()

        await browser.close()


async def parse_section(page, user_id: str, kp_id: str, section: str, status: str):
    total = 0
    for page_num in range(1, 100):
        url = f"https://www.kinopoisk.ru/user/{kp_id}/{section}/?page={page_num}"
        print(f"  {url}")

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception as e:
            print(f"    Ошибка навигации: {e}")
            break

        # Проверяем, не редиректнуло ли нас (конец списка)
        current_url = page.url
        if f"page={page_num}" not in current_url and page_num > 1:
            print("    Редирект на другую страницу — конец списка")
            break

        # Ждём прогрузки контента
        await page.wait_for_timeout(3000)

        # Проверяем капчу
        try:
            captcha = await page.wait_for_selector(
                ".CheckboxCaptcha, .captcha, [data-testid='checkbox-captcha'], .TextCaptcha",
                timeout=5000,
                state="visible"
            )
            if captcha:
                print("    ОБНАРУЖЕНА КАПЧА! Реши вручную...")
                for i in range(60):
                    await page.wait_for_timeout(1000)
                    try:
                        captcha_gone = await page.query_selector(".CheckboxCaptcha, .captcha, [data-testid='checkbox-captcha']")
                        if not captcha_gone:
                            print("    Капча решена!")
                            break
                    except Exception:
                        break
                else:
                    print("    Капча не решена")
                    break
        except Exception:
            pass

        # Ждём появления фильмов/сериалов в DOM
        try:
            await page.wait_for_selector('a[href*="/film/"], a[href*="/series/"]', timeout=10000)
        except Exception:
            print("    Фильмы не появились в DOM")
            break

        # Извлекаем данные из DOM через JavaScript
        movies = await page.evaluate("""
            (status) => {
                const results = [];
                const seen = new Set();

                document.querySelectorAll('a[href*="/film/"], a[href*="/series/"]').forEach(a => {
                    const href = a.getAttribute('href');
                    const match = href.match(/\\/(film|series)\\/(\\d+)\\//);
                    if (!match) return;

                    const filmId = parseInt(match[2]);
                    if (seen.has(filmId)) return;
                    seen.add(filmId);

                    // Ищем ближайший контейнер с img
                    let container = a;
                    for (let i = 0; i < 6; i++) {
                        container = container.parentElement;
                        if (!container) break;
                        if (container.querySelector('img')) break;
                    }
                    if (!container) container = a;

                    let title = '';
                    let year = null;
                    let poster = '';
                    let userRating = null;

                    const img = container.querySelector('img');
                    if (img) {
                        poster = img.src || '';
                        if (img.alt) {
                            // Формат: "Название. Год, жанр" или "Название. Год"
                            const altMatch = img.alt.match(/^(.+?)\\.\\s*(\\d{4})/);
                            if (altMatch) {
                                title = altMatch[1].trim();
                                year = parseInt(altMatch[2]);
                            } else {
                                title = img.alt;
                            }
                        }
                    }

                    // Если title не получили из alt — пробуем текст ссылки
                    if (!title && a.textContent) {
                        title = a.textContent.trim();
                    }

                    // Для watched ищем оценку пользователя
                    if (status === 'watched') {
                        const allSpans = container.querySelectorAll('span');
                        for (const span of allSpans) {
                            const text = span.textContent.trim();
                            if (/^\\d+$/.test(text)) {
                                const num = parseInt(text);
                                if (num >= 1 && num <= 10) {
                                    // Проверяем, что рядом есть иконка звезды
                                    const parent = span.parentElement;
                                    if (parent && parent.innerHTML.includes('star')) {
                                        userRating = num;
                                        break;
                                    }
                                }
                            }
                        }
                    }

                    results.push({
                        kp_id: filmId,
                        title_ru: title || 'Без названия',
                        year: year,
                        poster_url: poster,
                        status: status,
                        user_rating: userRating
                    });
                });

                return results;
            }
        """, status)

        if not movies:
            print("    Страница пуста — конец списка")
            break

        conn = db.get_conn()
        for m in movies:
            db.save_movie(conn, m)
            db.save_user_movie(conn, user_id, m)
        conn.close()

        total += len(movies)
        print(f"    Страница {page_num}: {len(movies)}")

    print(f"    Всего сохранено: {total}")


if __name__ == "__main__":
    asyncio.run(parse_all())
