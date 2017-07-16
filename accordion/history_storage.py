import json
import os


MAX_HISTORY_FILE_SIZE = 1024 * 1024


class FileHistoryStorage:

    def __init__(self, base_path='.', max_size=MAX_HISTORY_FILE_SIZE):
        self._max_size = max_size
        self._base_path = base_path
        self._history = {}

    def _history_file_name(self, chat_id):
        return os.path.join(self._base_path, '{}-history.txt'.format(chat_id))

    def _truncate_file(self, chat_id):
        # Reduce the file size twice.
        file_name = self._history_file_name(chat_id)
        with open(file_name, 'r') as f:
            seek_pos = int(self._max_size / 2)
            f.seek(seek_pos)
            f.readline()
            lines = f.readlines()

        self._history[chat_id] = {}
        copy_file_name = '{}.copy'.format(file_name)
        with open(copy_file_name, 'w') as f:
            for line in lines:
                f.write(line)
                # Reload the in-memory cache too.
                self._history[chat_id].update(json.loads(line.strip()))

        os.rename(copy_file_name, file_name)

    def _load_records(self, chat_id):
        self._history[chat_id] = {}
        try:
            with open(self._history_file_name(chat_id), 'r') as f:
                for line in f.readlines():
                    self._history[chat_id].update(json.loads(line.strip()))
        except:
            pass

    def add_record(self, chat_id, payload_hash, data):
        if not chat_id in self._history:
            self._load_records(chat_id)
        self._history[chat_id][payload_hash] = data

        json_payload = json.dumps({ payload_hash: data })
        file_name = self._history_file_name(chat_id)
        with open(file_name, 'a') as f:
            f.write('{}\n'.format(json_payload))
            file_stat = os.fstat(f.fileno())
            file_size = file_stat.st_size
        if file_size >= self._max_size:
            self._truncate_file(chat_id)

    def get_record(self, chat_id, payload_hash):
        if not chat_id in self._history:
            self._load_records(chat_id)
        return self._history[chat_id].get(payload_hash)
