from accordion.utils import (calculate_hash, normalize_url)
from urllib.parse import urlparse

class YouTubeUrlHashProvider:

    YOUTUBE_HOSTS = [
        'youtube.com',
        'youtu.be'
    ]

    def is_url_applicable(self, url):
        parsed_url = urlparse(normalize_url(url, schema='https'))
        for host in self.YOUTUBE_HOSTS:
            if host in parsed_url.netloc:
                return True
        return False

    def calculate_url_hash(self, url):
        parsed_url = urlparse(normalize_url(url, schema='https'))
        if 'youtu.be' in parsed_url.netloc:
            return calculate_hash(parsed_url.path[1:].encode())
        else:
            query = parsed_url.query
            for param in query.split('&'):
                key, value = param.split('=')
                if key == 'v':
                    return calculate_hash(value.encode())
        return None
