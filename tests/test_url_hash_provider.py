from accordion.url_hash_provider import YouTubeUrlHashProvider
import pytest


@pytest.mark.parametrize('url,is_applicable,expected_hash', [
    ('https://www.youtube.com/watch?v=CstiIq4imWM&t=1467s', True,
     '2deb6d6f02f2f0b42692159ec543cca5b84dd068'),
    ('youtube.com/watch?v=CstiIq4imWM', True,
     '2deb6d6f02f2f0b42692159ec543cca5b84dd068'),
    ('youtu.be/CstiIq4imWM', True,
     '2deb6d6f02f2f0b42692159ec543cca5b84dd068'),
    ('https://youtu.be/CstiIq4imWM', True,
     '2deb6d6f02f2f0b42692159ec543cca5b84dd068'),
    ('https://m.youtube.com/watch?v=CstiIq4imWM', True,
     '2deb6d6f02f2f0b42692159ec543cca5b84dd068'),
    ('m.youtube.com/watch?v=CstiIq4imWM', True,
     '2deb6d6f02f2f0b42692159ec543cca5b84dd068'),
    ('randomhost.com/something?param=1', False, None),
    ('https://randomhost.com/something?param=1', False, None),
])
def test_youtube_url_hash_provider(url, is_applicable, expected_hash):
    provider = YouTubeUrlHashProvider()
    assert provider.is_url_applicable(url) == is_applicable
    assert provider.calculate_url_hash(url) == expected_hash
