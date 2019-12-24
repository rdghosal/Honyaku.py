#!usr/bin/env/python3
import os, sys, requests, argparse, re, csv
from datetime import date
from bs4 import BeautifulSoup
from textblob import TextBlob, download_corpora
from textblob.exceptions import MissingCorpusError, MissingCorpusException

from .scrapequeue import ScrapeQueue
from .util import verify_dir, verify_url, clean_text, detect_lang, yank_hrefs


def check_spelling(text_dict):
    """
    Checks text_dict and iterates over every word using NLTK,
    reporting words that might need revision
    """ 
    for page, text in text_dict.items():
        print(f"Possible spelling errors in {page}:")
        # Iterate over words in lines in text for the page
        for line in text:
            line = line.lower()
            blob = TextBlob(line)
            try:
                for word in blob.words:
                    correction = word.spellcheck()[0]
                    # Report only if confidence higher than 75%
                    if correction[1] > 0.75:
                        print(f"  Word: {word} | Suggested Correction: {correction[0]}")

            except MissingCorpusError or MissingCorpusException:
                # Get user consent to download missing corpus for NLTK
                while True:
                    print("Current system is missing packages to complete spell check.")
                    consent = input("Allow download of package 'punkt' to system? (y/n) ")
                    if consent.lower() in ["y", "n"]: 
                        break

                if consent == "n": 
                    return -3
                try:
                    # Download packages for basic functionality
                    download_corpora.download_lite()
                    check_spelling(text_dict) # Try again
                except:
                    print("Error occured in package download.\n\
                           Check system or internet settings and try again.")
                    return -4

    return 0        


def _to_csv(fout, text_dict, lang):
    """
    Saves scraped output text to a CSV file
    formatted to allow side-by-side translations.
    """
    # Encoding set to utf-8 to allow for different charsets
    writer = csv.DictWriter(fout, fieldnames=[lang, "English"])
    writer.writeheader()
    for k in text_dict.keys():
        print(f"  Writing lines scraped from page {k}")
        fout.write(k.upper() + "\n") # To make clear what page is being written
        for line in text_dict[k]:
            writer.writerow({lang: line, "English": ""})


def _to_txt(fout, text_dict, lang):
    """
    Saves scraped output text to a textfile
    formatted to allow a 'staggered' view for the translation.
    """
    for k in text_dict.keys():
        print(f"  Writing lines scraped from page {k}")
        fout.write(k.upper() + "\n")
        for line in text_dict[k]:
            fout.write(f"{lang}: {line}\n")
            fout.write(f"English: \n\n")
        fout.write("==========\n\n") # To separate from next page


def save_scrapings(root, dir_, format_, text_dict, lang):
    """
    Saves scraping output as local file
    """
    # Format output file path as dir/dd-MM-yy_baseUrl.ext
    ext = format_
    today = date.strftime(date.today(), "%d-%m-%y")
    try:
        base_url = re.search(r"https?://www\.(.+)\.", root).group(1)
    except AttributeError:
        print("Failed to parse URL and assign filename to output file.")
        return -3

    # Arrange pat for output path
    path = os.path.join(dir_, f"{today}_{base_url}.{ext}")
    print(f"Writing {os.path.split(path)[1]} to {os.path.split(path)[0]}")

    try:
        with open(path, "w", encoding="utf-8", newline="") as fout:
            if format_ == "csv":
                _to_csv(fout, text_dict, lang)
            else:
                _to_txt(fout, text_dict, lang)
    except:
        print(f"Failed to save scrapings to {path}.\n\
                Check system configurations and try again.")
        return -4

    print(f"Scraped webpages saved to {path}")
    return 0


def scrape_webpage(root, dir_, format_, lang="", needs_check=False):
    """
    Navigates to input URL and parses HTML for relative links,
    scraping each page for its text
    """
    text_dict = dict()
    queue = ScrapeQueue(root)

    while len(queue) > 0:
        # Get html data from url on queue
        url = queue.dequeue()

        print(f"Scraping {url}...")
        r = requests.get(url)

        # Log bad request to console
        if not r.status_code == 200:
            print(f"Failed to scrape {url}.\n Status code: {r.status_code}\n")
            continue
        
        # Using lmxl parser and utf-8 to account for various charsets
        soup = BeautifulSoup(r.content, "lxml", from_encoding="utf-8")
        hrefs = yank_hrefs(root, url, soup.find_all("a")) # set instance
        if not hrefs:
            print(f"Error occured in scraping links from {url}.\n\
                    Check status of chromedriver executable and try again.")
            return -2

        # Add found links to queue
        for h in hrefs:
            queue.enqueue(h)

        # Add contents to text_dict
        title = soup.get("title")
        text = soup.get_text(separator=",")        
        if not lang: 
            lang = detect_lang(text) # Set lang

        text_dict[title] = clean_text(text) # Text passed as generator to lower mem load
        print()

    if needs_check:
        return check_spelling(text_dict)

    return save_scrapings(root, dir_, format_, text_dict, lang)


def main(args):
    """
    Takes argparse arguments object,
    and returns exit code based on success of selected process.
    """    
    if verify_url(args.url) and verify_dir(args.directory):
       return scrape_webpage(root=args.url, dir_=args.directory, format_=args.format,\
                             lang=args.language, needs_check=args.check) 

    return -1


if __name__ == "__main__":
    desc = """
            Honyaku.py assists webpage translation
            by scraping the input URL and all unique relative links therewithin
            of their text.
            Honyaku.py can also reports grammar and spelling errors post-translation--
            a useful feature for translators pressed for time.
            """
    # Default values for optional args
    default_dir = os.path.join(os.getenv("HOME"), "honyaku_output")
    default_format = "txt"

    # Initialize parser
    parser = argparse.ArgumentParser(description=desc)

    # Positional args
    parser.add_argument("url", help="Root url for scraping")

    # Optional args
    parser.add_argument("-L", "--language", nargs=1, type=str,\
                        help="Language of the webpage to be translated.")
    parser.add_argument("-f", "--format", choices=["csv", "txt"], nargs=1, default=default_format,\
                        help="Format of the scraped ouput. Defaults to textfile.")
    parser.add_argument("-d", "--directory", nargs=1, type=str, default=default_dir,\
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