import hashlib

def calculate_hash(payload):
    sha = hashlib.sha1()
    sha.update(payload)
    return sha.hexdigest()
