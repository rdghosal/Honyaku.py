import pytest
import honyaku.util as util


# To be used as test params
test_urls = ["www.url.com", "https://url.com", "http://www.url.jp"]

@pytest.mark.parametrize(
    "url, expected",
    [(test_urls[0], False), (test_urls[1], False), (test_urls[2], True)]
)
def test_verify_url(url, expected):
    # Execute
    actual = util.verify_url(url)
    # Verify
    assert actual == expected


@pytest.mark.parametrize(
    "url, expected",
    [(test_urls[0], pytest.raises(util.InvalidURLError)), (test_urls[1], util.InvalidURLError), (test_urls[2], test_urls[2][:] + "/")]
)
def test_correct_url(url, expected):
    # # Execute
    # actual = util.correct_url(url)
    # Verify
    assert util.correct_url(url) == expected

