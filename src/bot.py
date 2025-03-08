import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from dotenv import load_dotenv

from .services.gigachat_service import GigaChatService
from .services.subtitle_service import OpenSubtitlesService
from .services.channel_service import TelegramChannelManager
from .services.database_service import SQLiteMovieDatabase

class BotStates(StatesGroup):
    choosing_level = State()
    in_level_menu = State()

class MovieRecommenderBot:
    def __init__(self):
        load_dotenv()
        logging.basicConfig(level=logging.INFO)
        
        # Инициализация бота
        self.bot = Bot(token=os.getenv("BOT_TOKEN"))
        self.storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=self.storage)
        
        # Инициализация сервисов
        self.movie_db = SQLiteMovieDatabase()
        self.movie_recommender = GigaChatService(self.movie_db)
        self.subtitle_finder = OpenSubtitlesService()
        self.channel_manager = TelegramChannelManager()
        
        # Регистрация хэндлеров
        self._register_handlers()

    def _register_handlers(self):
        self.dp.register_message_handler(self._cmd_start, commands=['start'])
        self.dp.register_message_handler(
            self._process_level_selection,
            state=BotStates.choosing_level
        )
        self.dp.register_message_handler(
            self._process_back,
            lambda msg: msg.text == "Назад",
            state=BotStates.in_level_menu
        )
        self.dp.register_message_handler(
            self._process_generate,
            lambda msg: msg.text == "Сгенерировать",
            state=BotStates.in_level_menu
        )

    def _get_level_keyboard(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            types.KeyboardButton("A1"), types.KeyboardButton("A2"),
            types.KeyboardButton("B1"), types.KeyboardButton("B2"),
            types.KeyboardButton("C1"), types.KeyboardButton("C2")
        )
        return keyboard

    def _get_level_menu_keyboard(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton("Сгенерировать"))
        keyboard.add(types.KeyboardButton("Назад"))
        return keyboard

    async def _cmd_start(self, message: types.Message, state: FSMContext):
        await message.answer(
            "Привет! Выберите ваш уровень английского языка:",
            reply_markup=self._get_level_keyboard()
        )
        await BotStates.choosing_level.set()

    async def _process_level_selection(self, message: types.Message, state: FSMContext):
        level = message.text
        if not self.channel_manager.get_channel_link(level):
            await message.answer("Пожалуйста, выберите уровень, используя кнопки.")
            return

        await state.update_data(current_level=level)
        
        # Получаем последние 5 фильмов из БД
        movies = await self.movie_db.get_movies(level)
        if len(movies) > 5:
            movies = movies[:5]
        movies_text = "\n".join(movies) if movies else "Пока нет рекомендаций"
        
        await message.answer(
            f"Вот ссылка на канал для уровня {level}:\n"
            f"{self.channel_manager.get_channel_link(level)}\n\n"
            f"Последние рекомендованные фильмы:\n{movies_text}\n\n"
            "Хотите получить новую рекомендацию?",
            reply_markup=self._get_level_menu_keyboard()
        )
        await BotStates.in_level_menu.set()

    async def _process_back(self, message: types.Message, state: FSMContext):
        await message.answer(
            "Выберите ваш уровень английского языка:",
            reply_markup=self._get_level_keyboard()
        )
        await BotStates.choosing_level.set()

    async def _process_generate(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        current_level = data.get('current_level')
        
        if not current_level:
            await message.answer("Пожалуйста, сначала выберите уровень.")
            await BotStates.choosing_level.set()
            return
        
        await message.answer("Генерирую рекомендацию фильма...")
        
        try:
            # Получаем и сохраняем рекомендацию
            movie_name = await self.movie_recommender.get_recommendation(current_level)
            await self.movie_db.save_movie(current_level, movie_name)
            
            # Ищем субтитры
            subtitle_links = await self.subtitle_finder.find_subtitles(movie_name)
            
            # Формируем сообщение
            response_message = f"Рекомендованный фильм: {movie_name}"
            if subtitle_links:
                response_message += "\n\nСсылки на субтитры:"
                for link in subtitle_links:
                    response_message += f"\n{link}"
                response_message += "\nЕСЛИ СТРАНИЦА ЗАВИСЛА, ПЕРЕЗАГРУЗИТЕ ЕЁ"
            else:
                response_message += "\n\nК сожалению, субтитры не найдены."

            # Отправляем сообщения
            await message.answer(response_message)
            
            channel_id = self.channel_manager.get_channel_id(current_level)
            if channel_id:
                await self.bot.send_message(channel_id, response_message)
                
        except Exception as e:
            await message.answer("Произошла ошибка при генерации рекомендации. Попробуйте позже.")
            logging.error(f"Error in movie generation: {e}", exc_info=True)

    async def start(self):
        try:
            await self.movie_db.init_db()
            await self.dp.start_polling()
        finally:
            await self.bot.session.close()

if __name__ == "__main__":
    bot = MovieRecommenderBot()
    import asyncio
    asyncio.run(bot.start())