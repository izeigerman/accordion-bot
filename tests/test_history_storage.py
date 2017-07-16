import os
import json
from accordion.history_storage import FileHistoryStorage



def test_file_storage_add_and_return_records(tmp_directory):
    storage = FileHistoryStorage(base_path=tmp_directory)
    payload_hash = 'hash'
    chat_id = 'chat_id1'
    data = {'data': 'test'}
    storage.add_record(chat_id, payload_hash, data)

    actual_data = storage.get_record(chat_id, payload_hash)
    assert actual_data == data

    assert storage.get_record(chat_id, 'missing_hash') == None
    assert storage.get_record('wrong_chat_id', 'missing_hash') == None

    history_file_name = os.path.join(tmp_directory, '{}-history.txt'.format(chat_id))
    with open(history_file_name, 'r') as f:
        lines = f.readlines()
        assert(len(lines) == 1)
        line = lines[0].strip()
        assert line == json.dumps({payload_hash: data})

    # Test file reading.
    new_storage = FileHistoryStorage(base_path=tmp_directory)
    loaded_data = storage.get_record(chat_id, payload_hash)
    assert loaded_data['data'] == 'test'


def test_file_storage_truncate_file(tmp_directory):
    storage = FileHistoryStorage(base_path=tmp_directory, max_size=1024)
    payload_hash = 'hash'
    chat_id = 'chat_id2'
    data = {'data': 'test'}
    for i in range(0, 2000):
        storage.add_record(chat_id, '{}-{}'.format(payload_hash, i), data)

    first_remaining_hash_id = 1977
    for i in range(0, 2000):
        payload_hash_i = '{}-{}'.format(payload_hash, i)
        if i < first_remaining_hash_id:
            assert storage.get_record(chat_id, payload_hash_i) == None
        else:
            assert storage.get_record(chat_id, payload_hash_i) == data

    history_file_name = os.path.join(tmp_directory, '{}-history.txt'.format(chat_id))
    with open(history_file_name, 'r') as f:
        lines = f.readlines()
        assert(len(lines) == 23)
        line = lines[0].strip()
        first_hash = '{}-{}'.format(payload_hash, first_remaining_hash_id)
        assert line == json.dumps({first_hash: data})



