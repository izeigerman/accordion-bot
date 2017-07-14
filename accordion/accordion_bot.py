import hashlib
import urllib.request
import random
import re
from accordion.history_storage import FileHistoryStorage
from telegram.ext import (CommandHandler, MessageHandler, Filters, Updater)


class ContentHandler:

    def __init__(self):
        self._content = None

    def write(self, data):
        self._content = data

    @property
    def content(self):
        return self._content


class AccordionBot:

    def __init__(self, token, reactions_file, storage=FileHistoryStorage()):
        self._token = token
        self._payloads = {}
        self._history_storage = storage
        self._reactions = self._load_lines(reactions_file)

    def _chat_id_str(self, id):
        return '%02X' % (id & 0xFFFFFFFF)

    def _load_lines(self, file_name):
        try:
            with open(file_name, 'r') as f:
                lines = f.readlines()
                return [x.strip() for x in lines]
        except:
            return []

    def _create_payload_record(self, update):
        return {
            'originator_message_id': update.message.message_id,
            'originator_username': update.message.from_user.username
        }

    def _calculate_hash(self, payload):
        sha = hashlib.sha1()
        sha.update(payload)
        return sha.hexdigest()

    def _url_payload_hash(self, url):
        with urllib.request.urlopen(url) as response:
            return self._calculate_hash(response.read())

    def _add_new_payload(self, payload_hash, update):
        chat_id = self._chat_id_str(update.message.chat_id)
        history_record = self._create_payload_record(update)
        self._payloads[chat_id][payload_hash] = history_record
        self._history_storage.add_record(chat_id=chat_id, payload_hash=payload_hash,
                                         data=history_record)

    def _is_retro(self, new_hash, update):
        return new_hash in self._payloads[self._chat_id_str(update.message.chat_id)]

    def _on_retro(self, bot, update, retro_hash):
        if len(self._reactions) > 0:
            random_reaction = random.choice(self._reactions)
            bot.send_message(chat_id=update.message.chat_id, text=random_reaction,
                             reply_to_message_id=update.message.message_id)

    def _start_bot(self, bot, update):
        chat_id = self._chat_id_str(update.message.chat_id)
        self._payloads[chat_id] = self._history_storage.load_records(chat_id=chat_id)
        bot.send_message(chat_id=update.message.chat_id, text='Affirmative')

    def _on_text(self, bot, update):
        if self._chat_id_str(update.message.chat_id) not in self._payloads:
            return

        url = re.search('(?P<url>https?://[^\s]+)', update.message.text)
        if url:
            url = url.group('url')
            url_hash = self._calculate_hash(url.encode())
            if self._is_retro(url_hash, update):
                self._on_retro(bot, update, url_hash)
            else:
                self._add_new_payload(url_hash, update)
                payload_hash = self._url_payload_hash(url)
                if self._is_retro(payload_hash, update):
                    self._on_retro(bot, update, payload_hash)
                else:
                    self._add_new_payload(payload_hash, update)

    def _on_file(self, bot, update):
        if self._chat_id_str(update.message.chat_id) not in self._payloads:
            return

        if update.message.document:
            document = bot.get_file(update.message.document.file_id)
        else:
            document = bot.get_file(update.message.photo[-1].file_id)
        handler = ContentHandler()
        document.download(out=handler)
        payload_hash = self._calculate_hash(handler.content)
        if self._is_retro(payload_hash, update):
            self._on_retro(bot, update, payload_hash)
        else:
            self._add_new_payload(payload_hash, update)

    def run_bot(self):
        updater = Updater(token=self._token)
        dispatcher = updater.dispatcher

        start_handler = CommandHandler('RunAccordion', self._start_bot)
        text_handler = MessageHandler(Filters.text, self._on_text)
        file_handler = MessageHandler(Filters.photo | Filters.document, self._on_file)

        dispatcher.add_handler(file_handler)
        dispatcher.add_handler(text_handler)
        dispatcher.add_handler(start_handler)

        updater.start_polling()
