import pytest, requests, os
from bs4 import BeautifulSoup
import honyaku.util as util


# ===============
# -- FIXTURES --
# ===============

# To be used as test params
test_urls = ["www.url.com", "https://url.com", "http://www.url.jp"]
test_dirs = ["c:/users", "c:/users/rdb/documents/test.docx"]

# Setup / Teardown
@pytest.fixture(scope="module")
def anchors():
    r = requests.get(os.getenv("URL"))
    soup = BeautifulSoup(r.content, "html.parser")
    return soup.find_all("a")

@pytest.fixture(scope="module")
def url():
    return os.getenv("URL")

@pytest.fixture(scope="module")
def root():
    return os.getenv("ROOT")


# =================
# -- TEST CASES --
# =================

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
    [(test_urls[0], pytest.raises(util.InvalidURLError)), \
     (test_urls[1], pytest.raises(util.InvalidURLError))]
)
def test_correct_url_force_error(url, expected):
    # Verify
    with pytest.raises(util.InvalidURLError):
        util.correct_url(url) == expected


@pytest.mark.parametrize("url", [test_urls[2]])
def test_correct_url_ok(url):
    actual = util.correct_url(url) 
    assert actual == url + "/"


@pytest.mark.parametrize(
    "dir_, expected",
    [(test_dirs[0], True), (test_dirs[1], False)]
)
def test_verify_dir(dir_, expected):
    # Execute
    assert util.verify_dir(dir_) == expected


def test_yank_hrefs_via_driver(root, url, anchors):
    hrefs = util.yank_hrefs(root, url, anchors)
    for href in hrefs:
        assert not href.startswith("http")


@pytest.mark.parametrize("text, expected", [("//bar,[[foo,baz", "baz")])
def test_clean_text(text1, expected):
    # Execute
    clean_text = util.clean_text(text)
    # Verify
    actual = []
    for text in clean_text: actual.append(text)
    assert len(actual) == 1 and expected in actual


@pytest.mark.parametrize(
    "text, expected", 
    [
        (u"おはようございます！", "ja"),
        (u"大家好,今日は寒いですね！,那是大熊猫吗？", "zh-CN"),
        ("Testing English", "en")
    ]
)
def test_clean_text(text, expected):
    # Execute
    actual = util.detect_lang(text)
    # Verify
    assert actual == expected