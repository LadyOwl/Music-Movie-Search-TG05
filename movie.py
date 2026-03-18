import aiohttp
from config import TMDB_KEY

BASE_URL = "https://api.themoviedb.org/3"


async def search_movie(movie_name: str):
    """Поиск фильма в TMDB"""
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_KEY,
        "query": movie_name,
        "language": "ru-RU",
        "region": "RU",
        "include_adult": "false",
        "page": 1
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

        if data.get("results"):
            return data["results"][:5]
        return None
    except Exception as e:
        print(f"❌ Ошибка TMDB: {e}")
        return None


async def get_movie_details(movie_id: int):
    """Получение подробной информации о фильме с постером и ссылками"""
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_KEY,
        "language": "ru-RU",
        "append_to_response": "videos,external_ids"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
        return data
    except Exception as e:
        print(f"❌ Ошибка TMDB: {e}")
        return None


def get_poster_url(poster_path: str) -> str:
    """Формирование ссылки на постер высокого качества"""
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return ""


def get_watch_providers(movie_id: int) -> str:
    """Формируем ссылку на TMDB для просмотра где доступен фильм"""
    return f"https://www.themoviedb.org/movie/{movie_id}"


async def get_movie_with_poster(movie_name: str):
    """Поиск фильма с постером и деталями"""
    movies = await search_movie(movie_name)
    if not movies:
        return None

    # Берем первый результат
    movie = movies[0]
    movie_id = movie.get("id")

    # Получаем дополнительные детали
    details = await get_movie_details(movie_id) if movie_id else None

    return {
        "title": movie.get("title", "N/A"),
        "year": movie.get("release_date", "N/A")[:4] if movie.get("release_date") else "N/A",
        "rating": movie.get("vote_average", "N/A"),
        "overview": movie.get("overview", "Описание недоступно"),
        "poster": get_poster_url(movie.get("poster_path")),
        "tmdb_url": f"https://www.themoviedb.org/movie/{movie_id}" if movie_id else "",
        "imdb_id": details.get("external_ids", {}).get("imdb_id") if details else None,
        "youtube_trailer": None  # Заполним ниже
    }