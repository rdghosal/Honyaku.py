import pytest
from .scrapequeue import ScrapeQueue


# Setup / Teardown
@pytest.fixture(scope="module")
def squeue():
    """Queue instance to be used herein"""
    return ScrapeQueue("https://www.firsturl.com")


def test_sq_len(squeue):
    # Verify
    assert len(squeue) == 1


def test_sq_enqueue_same(squeue):
    """Adding duplicate url;
    should not be added to queue"""
    # Execute
    squeue.enqueue("https://www.firsturl.com")
    # Verify
    assert len(squeue) == 1


def test_sq_enqueue_internal(squeue):
    """Adding internal url
    should increase queue len by 1"""
    # Execute
    squeue.enqueue("cats.html")
    # Verify
    assert len(squeue) == 2


def test_sq_enqueue_external(squeue):
    """Adding unique url;
    should not increase queue len by 1"""
    # Execute
    squeue.enqueue("https://www.uniqueurl.com")
    # Verify
    assert len(squeue) == 2


def test_sq_dequeue(squeue):
    # Execute
    url = squeue.dequeue()
    # Verify
    assert url == "https://www.firsturl.com/"


def test_sq_postDequeue_len(squeue):
    # Verify
    assert len(squeue) == 1