from django.contrib import admin
from .models import Movie, UserMovie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('kp_id', 'title_ru', 'year', 'rating_kp', 'rating_imdb')
    search_fields = ('title_ru', 'title_en')
    list_filter = ('year', 'genres')


@admin.register(UserMovie)
class UserMovieAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'kp', 'status', 'user_rating')
    list_filter = ('status', 'user_id')
    search_fields = ('kp__title_ru',)
