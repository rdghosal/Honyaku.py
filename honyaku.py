#!usr/bin/env/python
import os, sys, requests, selenium, argparse, re, queue
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup


class ScrapeQueue():
    """Queue of unique URLs to be used for scraping"""
    def __init__(self, urls):
        # Ensure that only a set is passed
        self.__url_memo = set(urls) if not isinstance(urls, set) else url_set
        self.__queue = self._init_queue(self.__url_memo.copy())

    @property
    def memo(self):
        """Return memo of unique urls added to queue"""
        return self.__url_memo
    
    def _init_queue(self, url_set):
        """Instantiates queue"""
        q = queue.Queue()
        for url in url_set:
            q.put(url)            
        return q

    def pop(self):
        """Pops url off queue"""
        return self.__queue.pop()

    def add(self, url):
        """Adds url to queue if new"""
        if url not in self.__url_memo:
            self.__url_memo.add(url)
            self.queue.put(url)


def verify_url(url):
    """
    Uses re module and built-in str methods to check whether URL is valid
    """
    is_valid = False
    if re.search(r"^https?://", url) and re.search(r".*\.\w{2,3}/?$", url):
        is_valid = True

    return is_valid


def verify_dir(dir_):
    """
    Checks whether dir is an absolute path.
    Makes dir if not yet existing.
    """
    is_valid = False
    if os.path.isabs(dir_):
        is_valid = True
    if not os.path.exists(dir_):
        os.mkdir(dir_)
    
    return is_valid


def check_english(url):
    """
    Walks through provided URL,
    parsing text and using the Microsoft Word COM Object
    to verify grammar and spelling.
    """
    pass


def scrape_webpage(url, lang, format_):
    """
    Navigates to input URL and parses HTML for relative links,
    scraping each page for its text
    """
    # Get html from input url
    print(f"Sending request to {url}...")
    r = requests.get(url)

    # Handle bad request
    if not r.status_code == 200:
        print(f"Failed to scrape webpage.\n Status code: {r.status_code}")
        return -1 
    
    soup = BeautifulSoup(r.content, "html.parser")
    hrefs = pull_hrefs(soup.find_all("a")) # set instance
    


if __name__ == "__main__":
    desc = """
            Honyaku.py assists webpage translation
            by scraping the input URL and all unique relative links therewithin
            of their text.
            Honyaku.py can also reports grammar and spelling errors post-translation--
            a useful feature for translators pressed for time.
            """
    # Initialize parser
    parser = argparse.ArgumentParser(description=desc)

    # Positional args
    parser.add_argument("url", help="Root url for scraping")

    # Optional args
    parser.add_argument("-L", "--language", default="unknown", nargs=1,type=str,\
                        help="Language of the webpage to be translated.")
    parser.add_argument("-f", "--format", choices=["csv", "txt"], nargs=1, default="txt",\
                        help="Format of the scraped ouput. Defaults to textfile.")
    parser.add_argument("-d", --"directory", nargs=1, type=str, default=os.path.join(os.getenv("HOME"), "honyaku_output")\
                        help="Path to local directory for saving the output file")
    parser.add_argument("-c", "--check", action="store_true",\
                        help="Flag for whether input url is for check. Defaults to False.")

    # Retrieve user input
    exit_code = -1
    args = parser.parse_args()
    if verify_url(args.url) and verify_dir(args.directory):
        if args.check:
            exit_code = check_english(url=args.url)
        else:
            exit_code = scrape_webpage(url=args.url, lang=args.language, format_=args.format)

    # Print exit code and quit
    print(f"Finished program with exit code {exit_code}")
    _ = input("Press any key to quit the program.")

    sys.exit(exit_code)