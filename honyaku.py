#!usr/bin/env/python
import os, sys, requests, selenium, argparse, re, queue
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup


class ScrapeQueue():
    """Queue of unique URLs to be used for scraping"""
    def __init__(self, urls=set()):
        # Ensure that only a set is passed
        self.__url_memo = set(urls) if not isinstance(urls, set) else url_set
        self.__queue = self._init_queue(self.__url_memo.copy())

    def __len__(self):
        return len(self.__queue.queue)

    def _init_queue(self, url_set):
        """Instantiates queue"""
        q = queue.Queue()
        for url in url_set:
            q.put(url)            
        return q

    def pop(self):
        """Pops url off queue"""
        return self.__queue.pop()

    def push(self, url):
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
    if os.path.isabs(dir_) and os.path.isdir(dir_):
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

def save_scraping(dir_, format_, lang):
    """
    Saves scraping output as local file
    """
    # Format output
    ext = ".csv" if format_ == "csv" else ".txt"
    basename = "honyaku_output"
    path = os.path.join(dir_, filename + ext)
    
    if format_ == "csv":
        to_csv(path=path, text_dict=text_dict, lang=lang)
    else:
        to_txt(path=path, text_dict=text_dict, lang=lang)

def scrape_webpage(queue, format_, dir_, lang=""):
    """
    Navigates to input URL and parses HTML for relative links,
    scraping each page for its text
    """
    text_dict = dict()
    while len(queue) > 0:
        # Get html data from url on queue
        url = queue.pop()
        print(f"Scraping {url}...")
        r = requests.get(url)

        # Handle bad request
        if not r.status_code == 200:
            print(f"Failed to scrape {url}.\n Status code: {r.status_code}")
            return -1 
        
        soup = BeautifulSoup(r.content, "html.parser")
        hrefs = yank_rel_hrefs(soup.find_all("a")) # set instance
        
        # Add found links to queue
        for h in hrefs: queue.push(h)

        # Add contents to text_dict
        title = soup.get("title")
        text = soup.get_text()
        text_dict[title] = text
    
    save_scraping(dir_, text_dict, lang)
    


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
        q = ScrapeQueue(args.url)
        if args.check:
            exit_code = check_english(queue=q)
        else:
            exit_code = scrape_webpage(queue=q, lang=args.language,\
                                       format_=args.format, dir_=args.directory)

    # Print exit code and quit
    print(f"Finished program with exit code {exit_code}")
    _ = input("Press any key to quit the program.")

    sys.exit(exit_code)