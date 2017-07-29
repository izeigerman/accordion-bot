from accordion.utils import calculate_hash
from urllib.parse import urlparse

class YouTubeUrlHashProvider:

    YOUTUBE_HOSTS = [
        'youtube.com',
        'youtu.be'
    ]

    def _normalize_url(self, url):
        if not url.startswith('https://'):
            return 'https://{}'.format(url)
        else:
            return url

    def is_url_applicable(self, url):
        parsed_url = urlparse(self._normalize_url(url))
        for host in self.YOUTUBE_HOSTS:
            if host in parsed_url.netloc:
                return True
        return False

    def calculate_url_hash(self, url):
        parsed_url = urlparse(self._normalize_url(url))
        if 'youtu.be' in parsed_url.netloc:
            return calculate_hash(parsed_url.path[1:].encode())
        else:
            query = parsed_url.query
            for param in query.split('&'):
                key, value = param.split('=')
                if key == 'v':
                    return calculate_hash(value.encode())
        return None
