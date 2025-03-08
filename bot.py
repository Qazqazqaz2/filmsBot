import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

from .services.gigachat_service import GigaChatService
from .services.subtitle_service import OpenSubtitlesService
from .services.channel_service import TelegramChannelManager
from .services.message_service import TelegramMessageSender
from .services.state_service import TelegramStateManager

class BotStates(StatesGroup):
    choosing_level = State()
    in_level_menu = State()

class MovieRecommenderBot:
    def __init__(self):
        load_dotenv()
        
        # Настройка логирования
        logging.basicConfig(level=logging.INFO)
        
        # Инициализация бота и хранилища
        self.bot = Bot(token=os.getenv("BOT_TOKEN"))
        self.storage = MemoryStorage()
        self.dp = Dispatcher(self.bot, storage=self.storage)
        
        # Инициализация сервисов
        self.movie_recommender = GigaChatService()
        self.subtitle_finder = OpenSubtitlesService()
        self.channel_manager = TelegramChannelManager()
        self.message_sender = TelegramMessageSender(self.bot)
        
        # Регистрация хэндлеров
        self._register_handlers()

    def _register_handlers(self):
        """Register message handlers"""
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
        """Create level selection keyboard"""
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            types.KeyboardButton("A1"), types.KeyboardButton("A2"),
            types.KeyboardButton("B1"), types.KeyboardButton("B2"),
            types.KeyboardButton("C1"), types.KeyboardButton("C2")
        )
        return keyboard

    def _get_level_menu_keyboard(self):
        """Create level menu keyboard"""
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton("Сгенерировать"))
        keyboard.add(types.KeyboardButton("Назад"))
        return keyboard

    async def _cmd_start(self, message: types.Message):
        """Handle /start command"""
        await message.answer(
            "Привет! Выберите ваш уровень английского языка:",
            reply_markup=self._get_level_keyboard()
        )
        await BotStates.choosing_level.set()

    async def _process_level_selection(self, message: types.Message):
        """Handle level selection"""
        level = message.text
        if not self.channel_manager.get_channel_link(level):
            await message.answer("Пожалуйста, выберите уровень, используя кнопки.")
            return

        state_manager = TelegramStateManager(message.bot.get('state'))
        await state_manager.update_data(message.from_user.id, current_level=level)
        
        await message.answer(
            f"Вот ссылка на канал для уровня {level}:\n"
            f"{self.channel_manager.get_channel_link(level)}\n\n"
            "Не устраивают фильмы которые уже есть? Не проблема, сгенерируем",
            reply_markup=self._get_level_menu_keyboard()
        )
        await BotStates.in_level_menu.set()

    async def _process_back(self, message: types.Message):
        """Handle back button"""
        await message.answer(
            "Выберите ваш уровень английского языка:",
            reply_markup=self._get_level_keyboard()
        )
        await BotStates.choosing_level.set()

    async def _process_generate(self, message: types.Message):
        """Handle generate button"""
        state_manager = TelegramStateManager(message.bot.get('state'))
        user_data = await state_manager.get_data(message.from_user.id)
        current_level = user_data.get('current_level')
        
        await message.answer("Генерирую рекомендацию фильма...")
        
        try:
            # Получаем рекомендацию фильма
            movie_name = await self.movie_recommender.get_recommendation(current_level)
            
            # Ищем субтитры
            subtitle_links = await self.subtitle_finder.find_subtitles(movie_name)
            
            # Формируем сообщение
            response_message = f"Рекомендованный фильм: {movie_name}"
            if subtitle_links:
                response_message += "\n\nСсылки на субтитры:"
                for link in subtitle_links:
                    response_message += f"\n{link}"
            else:
                response_message += "\n\nК сожалению, субтитры не найдены."

            # Отправляем сообщение пользователю
            await self.message_sender.send_message(str(message.chat.id), response_message)
            
            # Отправляем в канал
            channel_id = self.channel_manager.get_channel_id(current_level)
            if channel_id:
                await self.message_sender.send_message(channel_id, response_message)
                
        except Exception as e:
            error_msg = "Произошла ошибка при генерации рекомендации. Попробуйте позже."
            await message.answer(error_msg)
            logging.error(f"Error in movie generation: {e}")
            logging.error(f"Traceback: {logging.traceback.format_exc()}")

    async def start(self):
        """Start the bot"""
        try:
            await self.dp.start_polling()
        finally:
            await self.bot.session.close()

if __name__ == "__main__":
    bot = MovieRecommenderBot()
    import asyncio
    asyncio.run(bot.start())