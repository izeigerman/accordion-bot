from accordion.utils import (normalize_url)
from urllib.parse import urlparse
import urllib.request
from http.client import HTTPConnection


class ShortLinkResolver:

    SHORT_LINK_PROVIDERS = [
        'bit.ly',
        'goo.gl'
    ]

    def is_short_link(self, url):
        parsed_url = urlparse(normalize_url(url))
        for host in self.SHORT_LINK_PROVIDERS:
            if host in parsed_url.netloc:
                return True
        return False

    def resolve_short_link(self, url):
        conn = None
        try:
            parsed_url = urlparse(normalize_url(url))
            conn = HTTPConnection(parsed_url.netloc)
            conn.request('GET', parsed_url.path)
            response = conn.getresponse()
            result = response.getheader('Location')
            return result
        except:
            return None
        finally:
            if conn:
                conn.close()
