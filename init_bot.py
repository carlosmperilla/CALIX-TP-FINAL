from bot.bot import run
from utils.logger import logger

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        logger.critical(f"Ha ocurrido un error en la ejecución del BOT: {e}")