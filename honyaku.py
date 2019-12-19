#!usr/bin/env/python
import os, sys, requests, argparse, re, queue, csv
from datetime import date
from bs4 import BeautifulSoup
from textblob import TextBlob, download_corpora
from textblob.exceptions import MissingCorpusError, MissingCorpusException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException


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

    def dequeue(self):
        """Pops url off queue"""
        return self.__queue.get()

    def enqueue(self, url):
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


def _yank_via_driver(url):
    """
    Uses Selenium à la Chrome to parse dynamic webpage for relative links
    """
    # TODO
    # Check path for Chrome driver before running up to here
    
    # Set up driver
    options = Options()
    options.add_argument("--headless") # Run headless
    options.binary_location = os.getenv("CHROME_DRIVER")

    # Init driver and pass set up
    browser = webdriver.Chrome(options=options)
    browser.get(url)

    # Get all anchors in the dynamic page
    # yield their respective href if relative
    anchors = browser.find_elements_by_tag_name("a")
    for a in anchors:        
        href = a.get_attribute("href")
        if href.find("http") == -1:
            yield href

    # Close driver process
    browser.quit()


def yank_rel_hrefs(anchors):
    """
    Returns a set of hrefs from a list of anchors
    """
    href_set = set()
    for anchor in anchors:
        href = anchor["href"]
        if href.find(".") == -1:
            # Faulty url found;
            # pass url to selenium driver for yanking
            for x in _yank_via_driver(url):
                href_set.add(x)
        elif href.find("http"): continue # Avoid external links
        else:
            href_set.add(anchor["href"])   

    return href_set


def clean_text(text):
    """
    Returns the input text after cleaning for extraneous spaces and symbols
    """
    # To convert into iterable
    text = text.split(",")

    # Regex for lines starting with special chars
    # all of which are set to empty strings to be filtered out later
    for line in text.split(","):
        line = line.strip() # Clean off empty space
        if re.search(r"^[\\\[\"\'\/]", text[line]):
            line = "" 
        if line: yield line

def detect_lang(text):
    """
    Uses Google Translate API to detect language
    """
    # Track frequencies of each language
    lang = ""
    lang_freqs = dict()
    try:
        for line in text.split(","):
            blob = TextBlob(line)
            lang = blob.detect_language()
            lang_freqs[lang] = lang_freqs.get(lang, 0) + 1 # + 1; set lang if not there
    except:
        print("Failed to connect to Google Translate and detect language.")
        print("WARNING: Consider checking Internet connection")
        return "Unknown"
    
    # Settle on the most frequent language
    for k, v in lang_freqs.items():
        highest = 0
        if v > highest:
            highest = v
            lang = k

    return lang


def check_spelling(text_dict):
    """
    Checks text_dict and iterates over every word using NLTK,
    reporting words that might need revision
    """ 
    for page, text in text_dict.items():
        print(f"Possible spelling errors in {page}:")
        # Iterate over words in lines in text for the page
        for line in text:
            blob = TextBlob(line)
            try:
                for word in blob.words:
                    for corrections in word.spellcheck():
                        # Report only if confidence lower than 75%
                        if corrections[0][1] < 0.75:
                            print(f"  Word: {word} | Suggested Correction: {corrections[0][0]}")

            except MissingCorpusError or MissingCorpusException:
                # Get user consent to download missing corpus for NLTK
                while True:
                    print("Current system is missing packages to complete spell check.")
                    consent = input("Allow download of package 'punkt' to system? (y/n) ")
                    if consent.lower() in ["y", "n"]: 
                        break

                if consent == "n": 
                    return -2
                try:
                    # Download packages for basic functionality
                    download_corpora.download_lite()
                except:
                    print("Error occured in package download.\
                        \nCheck system or internet settings and try again.")
                    return -3

    return 0        


def to_csv(fout, text_dict, lang):
    """
    Saves scraped output text to a CSV file
    formatted to allow side-by-side translations.
    """
    # Encoding set to utf-8 to allow for different charsets
    writer = csv.DictWriter(fout, fieldnames=[lang, "English"])
    writer.writeheader()
    for k in text_dict.keys():
        print(f"  Writing lines scraped from page {k}")
        writer.write(k.upper()) # To make clear what page is being written 
        for line in text_dict[k]:
            writer.writerow({lang: line, "English": ""})


def to_txt(fout, text_dict, lang):
    """
    Saves scraped output text to a textfile
    formatted to allow a 'staggered' view for the translation.
    """
    for k in text_dict.keys():
        fout.write(k.upper())
        print(f"  Writing lines scraped from page {k}")
        for line in text_dict[k]:
            fout.write(f"{lang}: {line}\n")
            fout.write(f"English: \n")
        fout.write("==========\n") # To separate from next page


def save_scrapings(root, dir_, format_, lang):
    """
    Saves scraping output as local file
    """
    # Format output file path
    # as dir/dd-MM-yy_baseUrl.ext
    ext = format_
    today = date.strftime(date.today(), "%d-%m-%y")
    base_url = re.search(r"https?://w?w?w?\.?(\d+)\.", root).group(1)
    path = os.path.join(dir_, f"{today}_{base_url}.{ext}")
    
    print(f"Writing {os.path.split(path)[1]} to {os.path.split(path)[0]}")

    try:
        with open(path, "w", encoding="utf-8") as fout:
            if format_ == "csv":
                to_csv(fout=fout, text_dict=text_dict, lang=lang)
            else:
                to_txt(fout=fout, text_dict=text_dict, lang=lang)
    except:
        print(f"Failed to save scrapings to {path}.\n\
                Check system configurations and try again.")
        return False

    print(f"Scraped webpage saved to {path}")
    return True


def scrape_webpage(queue, format_, dir_, lang=""):
    """
    Navigates to input URL and parses HTML for relative links,
    scraping each page for its text
    """
    root = ""
    text_dict = dict()

    while len(queue) > 0:
        # Get html data from url on queue
        url = queue.dequeue()
        if not root: root = url[:] # Use first item on queue as root

        print(f"Scraping {url}...")
        r = requests.get(url)

        # Log bad request to console
        if not r.status_code == 200:
            print(f"Failed to scrape {url}.\n Status code: {r.status_code}")
            continue 
        
        # Using lmxl parser and utf-8 to account for various charsets
        soup = BeautifulSoup(r.content, "lxml", from_encoding="utf-8")
        hrefs = yank_rel_hrefs(url, soup.find_all("a")) # set instance
        
        # Add found links to queue
        for h in hrefs: queue.enqueue(h)

        # Add contents to text_dict
        title = soup.get("title")
        text = soup.get_text(separator=",")
        if not lang: lang = detect_lang(text) # Set lang
        text_dict[title] = clean_text(text) # Text passed as generator to lower mem load
    
    if save_scrapings(root=root, dir_=dir_, text_dict=text_dict, lang=lang):
        return 0

    return -2


def main(args):
    """
    Takes argparse arguments object,
    and returns exit code based on success of selected process.
    """    
    exit_code = -1
    if verify_url(args.url) and verify_dir(args.directory):
        try:
            q = ScrapeQueue(args.url)
            if args.check:
                exit_code = check_spelling(queue=q)
            else:
                exit_code = scrape_webpage(queue=q, lang=args.language,\
                                        format_=args.format, dir_=args.directory)

    return exit_code


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
    parser.add_argument("-L", "--language", nargs=1,type=str,\
                        help="Language of the webpage to be translated.")
    parser.add_argument("-f", "--format", choices=["csv", "txt"], nargs=1, default="txt",\
                        help="Format of the scraped ouput. Defaults to textfile.")
    parser.add_argument("-d", "--directory", nargs=1, type=str, default=os.path.join(os.getenv("HOME"), "honyaku_output")\
                        help="Path to local directory for saving the output file")
    parser.add_argument("-c", "--check", action="store_true",\
                        help="Flag for whether input url is for check. Defaults to False.")

    # Retrieve user input
    args = parser.parse_args()
    exit_code = main(args)

    # Print exit code and quit
    print(f"Finished program with exit code {exit_code}")
    _ = input("Press any key to quit the program.")

    sys.exit(exit_code)