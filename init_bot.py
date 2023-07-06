from bot import Bot
from utils.logger import logger

if __name__ == "__main__":
    try:
        bot = Bot()
        bot.run()
    except Exception as e:
        logger.critical(f"Ha ocurrido un error en la ejecución del BOT: {e}")
        logger.exception(e)