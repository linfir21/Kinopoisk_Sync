from django.db import models


class Movie(models.Model):
    kp_id = models.IntegerField(primary_key=True)
    title_ru = models.CharField(max_length=500)
    title_en = models.CharField(max_length=500, blank=True, null=True)
    year = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)
    poster_url = models.URLField(blank=True, null=True)
    rating_kp = models.FloatField(blank=True, null=True)
    rating_imdb = models.FloatField(blank=True, null=True)
    genres = models.CharField(max_length=500, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)
    actors = models.TextField(blank=True, null=True)
    director = models.CharField(max_length=500, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'movies'

    def __str__(self):
        return self.title_ru


class UserMovie(models.Model):
    STATUS_CHOICES = [
        ('watched', 'Просмотрено'),
        ('watchlist', 'Буду смотреть'),
    ]

    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=50)
    kp = models.ForeignKey(Movie, on_delete=models.CASCADE, db_column='kp_id')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    user_rating = models.IntegerField(blank=True, null=True)
    watched_date = models.CharField(max_length=20, blank=True, null=True)
    synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_movies'
        unique_together = ('user_id', 'kp', 'status')

    def __str__(self):
        return f"{self.user_id} - {self.kp.title_ru} ({self.status})"
