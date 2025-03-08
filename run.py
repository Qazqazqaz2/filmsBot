import asyncio
import logging
from src.bot import MovieRecommenderBot

if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Создание и запуск бота
    bot = MovieRecommenderBot()
    
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
    except Exception as e:
        logging.error(f"Произошла ошибка: {e}", exc_info=True) 