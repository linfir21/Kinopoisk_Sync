from django.core.management.base import BaseCommand
from enricher import enrich_all


class Command(BaseCommand):
    help = 'Обогащает фильмы в базе данными из Kinopoisk API Unofficial'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=500,
            help='Максимальное количество фильмов для обогащения (по умолчанию 500)',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        self.stdout.write(self.style.NOTICE(f'Начинаем обогащение (limit={limit})...'))
        enrich_all(limit=limit)
        self.stdout.write(self.style.SUCCESS('Обогащение завершено!'))
