import logging
from accordion.accordion_bot import AccordionBot

TELEGRAM_TOKEN = '<INSERT_YOUR_TOKEN>'
REACTIONS_FILE = 'reactions_list.txt'

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
    bot = AccordionBot(token=TELEGRAM_TOKEN, reactions_file=REACTIONS_FILE)
    bot.run_bot()
