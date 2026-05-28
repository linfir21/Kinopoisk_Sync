from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Movie, UserMovie


USERS = settings.USERS


def index(request):
    users_data = {}
    for uid, udata in USERS.items():
        watched = UserMovie.objects.filter(user_id=uid, status='watched').select_related('kp')
        watchlist = UserMovie.objects.filter(user_id=uid, status='watchlist').select_related('kp')
        users_data[uid] = {
            "name": udata["name"],
            "watched": watched,
            "watchlist": watchlist
        }

    # Общие фильмы
    common_watchlist = get_common_movies('watchlist')
    common_watched = get_common_movies('watched')

    return render(request, 'movies/index.html', {
        'users': users_data,
        'common_watchlist': common_watchlist,
        'common_watched': common_watched,
        'users_config': USERS,
    })


def movie_detail(request, kp_id):
    movie = get_object_or_404(Movie, pk=kp_id)
    # Получаем оценки пользователей для этого фильма
    user_movies = UserMovie.objects.filter(kp_id=kp_id).select_related('kp')
    ratings = []
    for um in user_movies:
        if um.user_id in USERS:
            ratings.append({
                'uid': um.user_id,
                'name': USERS[um.user_id]['name'],
                'rating': um.user_rating,
            })
    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'actors': movie.actors or '',
        'ratings': ratings,
    })


def get_common_movies(status):
    """Фильмы, которые есть у обоих пользователей с указанным статусом."""
    user_ids = list(USERS.keys())
    if len(user_ids) < 2:
        return Movie.objects.none()

    u1, u2 = user_ids[0], user_ids[1]
    kp_ids_1 = UserMovie.objects.filter(user_id=u1, status=status).values_list('kp_id', flat=True)
    kp_ids_2 = UserMovie.objects.filter(user_id=u2, status=status).values_list('kp_id', flat=True)
    common_ids = set(kp_ids_1) & set(kp_ids_2)

    movies = Movie.objects.filter(kp_id__in=common_ids)
    # Добавляем оценки пользователей
    result = []
    for movie in movies:
        um1 = UserMovie.objects.filter(user_id=u1, kp_id=movie.kp_id, status=status).first()
        um2 = UserMovie.objects.filter(user_id=u2, kp_id=movie.kp_id, status=status).first()
        movie.user1_rating = um1.user_rating if um1 else None
        movie.user2_rating = um2.user_rating if um2 else None
        result.append(movie)
    return result
