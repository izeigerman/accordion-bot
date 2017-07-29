import hashlib

def calculate_hash(payload):
    sha = hashlib.sha1()
    sha.update(payload)
    return sha.hexdigest()


def normalize_url(url, schema='http'):
    if not url.startswith('http'):
        return '{}://{}'.format(schema, url)
    else:
        return url
