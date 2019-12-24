import pytest, os
from honyaku import honyaku, util


# ===============
# -- FIXTURES --
# ===============

# Setup for module-scope args
@pytest.fixture(scope="module")
def root():
    return os.getenv("ROOT")

@pytest.fixture(scope="module")
def dir_():
    # Same default path as in actual runtime
    return os.path.join(os.getenv("HOME"), "honyaku_output")

@pytest.fixture(scope="module")
def default_format():
    return "txt"

@pytest.fixture(scope="module")
def csv_format():
    return "csv"

@pytest.fixture(scope="module")
def lang():
    # Testing with unicode str for Japanese
    return u"日本語"

@pytest.fixture(scope="module")
def no_err_en_text_dict():
    td = {
        "home": ["The cow says moo"]
    }
    return td

@pytest.fixture(scope="module")
def err_en_text_dict():
    td = {
        "home": ["Teh coo saiz mo"]
    }
    return td

@pytest.fixture(scope="module")
def jp_text_dict():
    td = {
        "home": [u"牛がモーと言います", u"これもテスト"]
    }
    return td


# =================
# -- TEST CASES --
# =================

def test_check_spelling(err_en_text_dict):
    # Setup
    expected = 0
    # Execute 
    actual = honyaku.check_spelling(err_en_text_dict)
    # Verify
    assert actual == expected

def test_save_scrapings_txt(root, dir_, default_format, jp_text_dict, lang):
    # Setup
    expected = 0
    util.verify_dir(dir_) # make dir if not existing
    # Execute
    actual = honyaku.save_scrapings(root, dir_, default_format, jp_text_dict, lang)
    # Verify
    assert actual == expected


def test_save_scrapings_csv(root, dir_, csv_format, jp_text_dict, lang):
    # Setup
    expected = 0
    util.verify_dir(dir_) # make dir if not existing
    # Execute
    actual = honyaku.save_scrapings(root, dir_, csv_format, jp_text_dict, lang)
    # Verify
    assert actual == expected


# Essentially E2E test
def test_scrape_webpage_no_lang_no_check(root, dir_, default_format):
    # Setup 
    expected = 0
    # Execute
    actual = honyaku.scrape_webpage(root, dir_, default_format)
    # Verify
    assert actual == expected
    