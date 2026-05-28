import requests
import sqlite3
from config import DB_PATH, KP_API_KEY

API_URL = "https://kinopoiskapiunofficial.tech/api/v2.2/films/"

if not KP_API_KEY:
    print("WARNING: KP_API_KEY не задан. Добавьте его в .env (KP_API_KEY=ваш_ключ)")


def enrich_movie(kp_id: int):
    """Получает полные данные о фильме из API."""
    headers = {"X-API-KEY": KP_API_KEY}
    response = requests.get(f"{API_URL}{kp_id}", headers=headers, timeout=10)
    
    if response.status_code != 200:
        print(f"Ошибка API для {kp_id}: {response.status_code}")
        return None
    
    data = response.json()
    return {
        "kp_id": kp_id,
        "title_ru": data.get("nameRu"),
        "title_en": data.get("nameEn") or data.get("nameOriginal"),
        "year": data.get("year"),
        "description": data.get("description"),
        "short_description": data.get("shortDescription"),
        "poster_url": data.get("posterUrl"),
        "rating_kp": data.get("ratingKinopoisk"),
        "rating_imdb": data.get("ratingImdb"),
        "genres": ", ".join(g["genre"] for g in data.get("genres", [])),
        "duration": data.get("filmLength"),
        "director": ", ".join(
            p["nameRu"] or p["nameEn"]
            for p in data.get("staff", [])
            if p.get("professionKey") == "DIRECTOR"
        )
    }


def enrich_all(limit: int = 500):
    """Обогащает все фильмы в базе без описания."""
    if not KP_API_KEY:
        print("Ошибка: KP_API_KEY не задан. Добавьте его в .env")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT kp_id FROM movies WHERE description IS NULL LIMIT ?", (limit,))
    ids = [row[0] for row in c.fetchall()]

    for kp_id in ids:
        print(f"Обогащение {kp_id}...")
        data = enrich_movie(kp_id)
        if data:
            # Подтягиваем актёров отдельно
            actors = enrich_actors(kp_id)
            c.execute("""
                UPDATE movies SET
                    title_ru = COALESCE(?, title_ru),
                    title_en = COALESCE(?, title_en),
                    year = COALESCE(?, year),
                    description = ?,
                    short_description = ?,
                    poster_url = COALESCE(?, poster_url),
                    rating_kp = COALESCE(?, rating_kp),
                    rating_imdb = ?,
                    genres = ?,
                    duration = ?,
                    director = ?,
                    actors = ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE kp_id = ?
            """, (
                data["title_ru"], data["title_en"], data["year"],
                data["description"], data["short_description"],
                data["poster_url"], data["rating_kp"], data["rating_imdb"],
                data["genres"], data["duration"], data["director"],
                actors,
                kp_id
            ))
            conn.commit()

    conn.close()


def enrich_actors(kp_id: int):
    """Получает актёров (отдельный endpoint)."""
    headers = {"X-API-KEY": KP_API_KEY}
    response = requests.get(
        f"https://kinopoiskapiunofficial.tech/api/v1/staff?filmId={kp_id}",
        headers=headers, timeout=10
    )
    if response.status_code == 200:
        staff = response.json()
        actors = [
            f"{p.get('nameRu') or p.get('nameEn')} ({p.get('description', '')})"
            for p in staff
            if p.get("professionKey") == "ACTOR"
        ][:10]  # топ-10
        return ", ".join(actors)
    return ""


if __name__ == "__main__":
    enrich_all()