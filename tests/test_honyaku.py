import pytest
from honyaku import honyaku


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
        "home": [u"牛がモーと言います"]
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