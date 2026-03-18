import aiohttp
from config import LASTFM_KEY


async def search_artist(artist_name: str):
    """Поиск информации об исполнителе в Last.fm"""
    url = "https://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "artist.getinfo",
        "artist": artist_name,
        "api_key": LASTFM_KEY,
        "format": "json",
        "lang": "ru"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

        if "error" in data:
            return None

        artist_info = data["artist"]
        return {
            "name": artist_info.get("name", "Неизвестно"),
            "bio": artist_info.get("bio", {}).get("summary", "Описание недоступно"),
            "image": artist_info.get("image", [{}])[-1].get("#text", ""),
            "url": artist_info.get("url", ""),
            "tags": [tag["name"] for tag in artist_info.get("tags", {}).get("tag", [])[:5]]
        }
    except Exception as e:
        print(f"❌ Ошибка Last.fm: {e}")
        return None


async def search_track(track_name: str):
    """Поиск трека в Last.fm"""
    url = "https://ws.audioscrobbler.com/2.0/"
    params = {
        "method": "track.search",
        "track": track_name,
        "api_key": LASTFM_KEY,
        "format": "json",
        "limit": 5
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()

        if "error" in data:
            return None

        tracks = data["results"]["trackmatches"]["track"][:5]
        return tracks
    except Exception as e:
        print(f"❌ Ошибка Last.fm: {e}")
        return None