import urllib.request
import random
import re
from accordion.history_storage import FileHistoryStorage
from accordion.url_hash_provider import YouTubeUrlHashProvider
from accordion.utils import calculate_hash
from telegram.ext import (MessageHandler, Filters, Updater)
from PIL import Image
import imagehash


DEFAULT_ACCORDION_STICKERS = [
    'CAADAgAD0gUAAhDqYwP8zWf0qHJLaAI',
    'CAADAgAD1gUAAhDqYwM4xhvFG-zhgwI',
    'CAADAgAD1AUAAhDqYwPvj3VKQ9IIUQI',
    'CAADAgAD3gUAAhDqYwMi6Z1GdiI6mwI',
    'CAADAgAD3AUAAhDqYwMU0HsXnF8N0wI',
    'CAADAgAD8QUAAhDqYwMK0aVwKDmqvAI',
    'CAADAgAD4gUAAhDqYwON0hlqIPtuQgI',
    'CAADAgADzgUAAhDqYwN0n1SsVyNtzQI',
]


class ContentHandler:

    def __init__(self):
        self._content = None
        self._current_pos = 0

    def write(self, data):
        self._content = data
        self._current_pos = 0

    def tell(self):
        return self._current_pos

    def seek(self, pos):
        self._current_pos = pos

    def read(self, bytes=None):
        if self._current_pos >= len(self._content):
            return None
        if bytes:
            new_pos = self._current_pos + bytes
            if new_pos > len(self._content):
                new_pos = len(self._content)
            result = self._content[self._current_pos:new_pos]
            self._current_pos = new_pos
            return result
        else:
            new_pos = len(self._content)
            result =  self._content[self._current_pos:]
            self._current_pos = new_pos
            return result

    def close(self):
        pass

    @property
    def content(self):
        return self._content


class AccordionBot:

    URL_REGEXP = re.compile(
        'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        re.IGNORECASE)

    def __init__(self, token, reactions_file=None, stickers_file=None,
                 stickers=DEFAULT_ACCORDION_STICKERS, storage=FileHistoryStorage()):
        self._token = token
        self._history_storage = storage
        self._reactions = []
        self._stickers = []
        if reactions_file:
            self._reactions = self._load_lines(reactions_file)
        elif stickers_file:
            self._stickers = self._load_lines(stickers_file)
        else:
            self._stickers = stickers
        self._url_hash_providers = [
            YouTubeUrlHashProvider()
        ]

    def _chat_id_str(self, id):
        return '%02X' % (id & 0xFFFFFFFF)

    def _load_lines(self, file_name):
        try:
            with open(file_name, 'r') as f:
                lines = f.readlines()
                return [x.strip() for x in lines]
        except:
            return []

    def _create_history_record(self, update):
        return {
            'originator_message_id': update.message.message_id,
            'originator_user_name': update.message.from_user.username,
            'originator_user_id': update.message.from_user.id
        }

    def _calculate_hash(self, payload):
        return calculate_hash(payload)

    def _url_payload(self, url):
        with urllib.request.urlopen(url) as response:
            return response.read()

    def _store_new_record(self, payload_hash, update):
        chat_id = self._chat_id_str(update.message.chat_id)
        history_record = self._create_history_record(update)
        self._history_storage.add_record(chat_id=chat_id, payload_hash=payload_hash,
                                         data=history_record)

    def _find_retro(self, new_hash, update):
        chat_id = self._chat_id_str(update.message.chat_id)
        return self._history_storage.get_record(chat_id=chat_id, payload_hash=new_hash)

    def _calculate_payload_hash(self, payload):
        if isinstance(payload, ContentHandler):
            handler = payload
        else:
            handler = ContentHandler()
            handler.write(payload)
        try:
            return str(imagehash.average_hash(Image.open(handler), hash_size=10))
        except:
            return self._calculate_hash(handler.content)

    def _calculate_url_hash(self, url):
        for provider in self._url_hash_providers:
            if provider.is_url_applicable(url):
                return provider.calculate_url_hash(url)
        return self._calculate_hash(url.encode())

    def _on_retro(self, bot, update, retro_hash, retro_record):
        if len(self._reactions) > 0:
            random_reaction = random.choice(self._reactions)
            bot.send_message(chat_id=update.message.chat_id, text=random_reaction,
                             reply_to_message_id=update.message.message_id)
        else:
            random_sticker = random.choice(self._stickers)
            bot.send_sticker(chat_id=update.message.chat_id, sticker=random_sticker,
                             reply_to_message_id=update.message.message_id)
        bot.send_message(chat_id=update.message.chat_id, text='Proof',
                         reply_to_message_id=retro_record['originator_message_id'])

    def _on_text(self, bot, update):
        urls = self.URL_REGEXP.findall(update.message.text)
        if urls:
            url = urls[0]
            url_hash = self._calculate_url_hash(url)
            url_retro_record = self._find_retro(url_hash, update)
            if url_retro_record:
                self._on_retro(bot, update, url_hash, retro_record=url_retro_record)
            else:
                self._store_new_record(url_hash, update)
                payload = self._url_payload(url)
                payload_hash = self._calculate_payload_hash(payload)
                payload_retro_record = self._find_retro(payload_hash, update)
                if payload_retro_record:
                    self._on_retro(bot, update, payload_hash,
                                   retro_record=payload_retro_record)
                else:
                    self._store_new_record(payload_hash, update)

    def _on_file(self, bot, update):
        if update.message.document:
            document = bot.get_file(update.message.document.file_id)
        else:
            document = bot.get_file(update.message.photo[-1].file_id)
        handler = ContentHandler()
        document.download(out=handler)
        payload_hash = self._calculate_payload_hash(handler)
        payload_retro_record = self._find_retro(payload_hash, update)
        if payload_retro_record:
            self._on_retro(bot, update, payload_hash,
                           retro_record=payload_retro_record)
        else:
            self._store_new_record(payload_hash, update)

    def run_bot(self):
        updater = Updater(token=self._token)
        dispatcher = updater.dispatcher

        text_handler = MessageHandler(Filters.text, self._on_text)
        file_handler = MessageHandler(Filters.photo | Filters.document, self._on_file)

        dispatcher.add_handler(file_handler)
        dispatcher.add_handler(text_handler)

        updater.start_polling()
