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
            return data["results"][:5]  # Возвращаем топ-5
        return None
    except Exception as e:
        print(f"❌ Ошибка TMDB: {e}")
        return None


async def get_movie_details(movie_id: int):
    """Получение подробной информации о фильме"""
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": TMDB_KEY,
        "language": "ru-RU",
        "append_to_response": "videos,credits"
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
    """Формирование ссылки на постер"""
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return ""