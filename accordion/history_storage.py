import json


class FileHistoryStorage:

    def _history_file_name(self, chat_id):
        return '{}-history.txt'.format(chat_id)

    def add_record(self, chat_id, payload_hash, data):
        json_payload = json.dumps({ payload_hash: data })
        with open(self._history_file_name(chat_id), 'a') as f:
            f.write('{}\n'.format(json_payload))

    def load_records(self, chat_id):
        try:
            with open(self._history_file_name(chat_id), 'r') as f:
                result = {}
                for line in f.readlines():
                    result.update(json.loads(line.strip()))
                return result
        except:
            return {}
