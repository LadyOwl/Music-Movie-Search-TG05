import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import BOT_TOKEN
from keyboards import get_start_keyboard, get_back_keyboard
from music import search_artist, search_track
from movie import search_movie, get_movie_details, get_poster_url

# Инициализация бота и хранилища состояний
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Класс состояний для режимов поиска
class SearchMode(StatesGroup):
    waiting_for_music = State()
    waiting_for_movie = State()


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()  # Сбрасываем режим поиска

    user_name = message.from_user.first_name
    keyboard = get_start_keyboard()
    await message.answer(
        f"Привет, {user_name}! 👋\n\n"
        "Я помогу тебе найти:\n"
        "• 🎵 Музыку и исполнителей (Last.fm)\n"
        "• 🎬 Фильмы и сериалы (TMDB)\n\n"
        "Выбери, что искать:",
        reply_markup=keyboard
    )


# Кнопка "Найти музыку"
@dp.callback_query(F.data == "btn_music")
async def btn_music(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(SearchMode.waiting_for_music)
    await callback.message.answer(
        "🎵 **Режим: Поиск музыки**\n\n"
        "Отправь название исполнителя или трека.\n"
        "Чтобы выйти: /start\n\n"
        "⬅️ Или нажми /start в меню"
    )
    await callback.answer()


# Кнопка "Найти фильм"
@dp.callback_query(F.data == "btn_movie")
async def btn_movie(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(SearchMode.waiting_for_movie)
    await callback.message.answer(
        "🎬 **Режим: Поиск фильмов**\n\n"
        "Отправь название фильма.\n"
        "Чтобы выйти: /start\n\n"
        "⬅️ Или нажми /start в меню"
    )
    await callback.answer()


# Кнопка "Назад"
@dp.callback_query(F.data == "btn_back")
async def btn_back(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    keyboard = get_start_keyboard()
    await callback.message.edit_text(
        "Выбери, что искать:",
        reply_markup=keyboard
    )
    await callback.answer()


# Обработка текста - поиск в зависимости от режима
@dp.message(F.text)
async def handle_text(message: types.Message, state: FSMContext):
    text = message.text

    # Игнорируем команды
    if text.startswith('/'):
        return

    current_state = await state.get_state()

    # Режим поиска музыки
    if current_state == SearchMode.waiting_for_music:
        await message.answer(f"🔍 Ищу в музыке: {text}...")

        # Сначала пробуем найти исполнителя
        artist = await search_artist(text)
        if artist:
            bio = artist["bio"][:500] + "..." if len(artist["bio"]) > 500 else artist["bio"]
            tags = ", ".join(artist["tags"]) if artist["tags"] else "Нет данных"
            result = f"🎤 **{artist['name']}**\n\n📝 {bio}\n\n🏷️ Теги: {tags}\n\n🔗 {artist['url']}"

            if artist["image"]:
                await message.answer_photo(photo=artist["image"], caption=result)
            else:
                await message.answer(result)
        else:
            # Если не исполнитель — ищем трек
            tracks = await search_track(text)
            if tracks:
                result = "🎵 **Найдено треков:**\n\n"
                for i, track in enumerate(tracks, 1):
                    name = track.get('name', 'N/A')
                    artist_name = track.get('artist', 'N/A')
                    result += f"{i}. **{name}** — {artist_name}\n"
                await message.answer(result)
            else:
                await message.answer("❌ Не найдено. Попробуй другое название.")
        return

    # Режим поиска фильмов
    elif current_state == SearchMode.waiting_for_movie:
        await message.answer(f"🔍 Ищу фильм: {text}...")
        movies = await search_movie(text)

        if movies:
            result = "🎬 **Найдено фильмов:**\n\n"
            for i, movie in enumerate(movies, 1):
                title = movie.get("title", "N/A")
                year = movie.get("release_date", "N/A")[:4] if movie.get("release_date") else "N/A"
                rating = movie.get("vote_average", "N/A")
                overview = movie.get("overview", "Описание недоступно")
                if len(overview) > 100:
                    overview = overview[:100] + "..."
                result += f"{i}. **{title}** ({year}) ⭐ {rating}\n📝 {overview}\n\n"
            await message.answer(result)
        else:
            await message.answer("❌ Фильм не найден. Попробуй другое название.")
        return

    # Если режим не выбран — подсказка
    else:
        await message.answer(
            "❓ Сначала выбери, что искать:\n"
            "🎵 /start → Найти музыку\n"
            "🎬 /start → Найти фильм"
        )


# Обработка команды /movie (быстрый поиск без режима)
@dp.message(Command("movie"))
async def cmd_movie(message: types.Message):
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.answer("🎬 Используй: /movie <название фильма>\n\nПример: /movie Интерстеллар")
        return

    movie_name = args[1]
    await message.answer(f"🔍 Ищу фильм: {movie_name}...")

    movies = await search_movie(movie_name)

    if movies:
        result = "🎬 **Найдено фильмов:**\n\n"
        for i, movie in enumerate(movies, 1):
            title = movie.get("title", "N/A")
            year = movie.get("release_date", "N/A")[:4] if movie.get("release_date") else "N/A"
            rating = movie.get("vote_average", "N/A")
            overview = movie.get("overview", "Описание недоступно")
            if len(overview) > 100:
                overview = overview[:100] + "..."
            result += f"{i}. **{title}** ({year}) ⭐ {rating}\n📝 {overview}\n\n"
        await message.answer(result)
    else:
        await message.answer("❌ Фильм не найден. Попробуй другое название.")


# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    text = (
        "🤖 **Команды бота:**\n\n"
        "/start — главное меню\n"
        "/music — режим поиска музыки\n"
        "/movie <название> — поиск фильма\n"
        "/help — эта справка\n\n"
        "Также можно выбрать режим через кнопки в /start"
    )
    await message.answer(text)


# Запуск бота
async def main():
    print("🤖 Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())