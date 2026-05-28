import asyncio
from django.core.management.base import BaseCommand
from parser import parse_all


class Command(BaseCommand):
    help = 'Парсит оценки и списки фильмов с Кинопоиска'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Запуск парсера Кинопоиска...'))
        asyncio.run(parse_all())
        self.stdout.write(self.style.SUCCESS('Парсинг завершён!'))
