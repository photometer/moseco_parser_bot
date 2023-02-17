import datetime as dt
import logging
from os import getenv
from subprocess import PIPE, Popen
from sys import stdout
from time import sleep

from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

load_dotenv()

TELEGRAM_TOKEN = getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 3600
BOT_MESSAGE_TIMES = (0, 9, 12, 15, 18, 21)


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=stdout)
logger.addHandler(handler)


def send_message(bot, message):
    """Bot message sending."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message
        )
        logging.info(f'Бот отправил сообщение {message}')
    except TelegramError:
        logging.error('Сбой при отправке сообщения')


def main():
    """Main logic of a bot."""
    bot = Bot(token=TELEGRAM_TOKEN)
    counter = 1
    while True:
        logging.info('Ready to crawl again')
        _, err = Popen(['scrapy', 'crawl', 'moseco'], stderr=PIPE, text=True,
                       encoding='utf-8').communicate()
        if err:
            message = err.split('\n')[-2]
            logging.error(message)
            send_message(
                bot, f'Сбой в работе программы. Последняя ошибка:\n{message}'
            )
        logging.info('Everything is crawled')
        sleep(RETRY_TIME)
        current_datetime = dt.datetime.now()
        if current_datetime.hour in BOT_MESSAGE_TIMES:
            message = (f'Cводка за текущий период: {counter} раз(a) '
                       'пауки делали свое дело.')
            send_message(bot, message)
            counter = 1
        else:
            counter += 1


if __name__ == '__main__':
    main()
