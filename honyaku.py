#!usr/bin/env/python
import os, sys, requests, selenium, argparse
from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup

def main():
    pass

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
    parser.add_argument("-L", "--language", help="Original language", default="unknown", nargs=1,\
                         type="str", help="Language of the webpage to be translated.")
    parser.add_argument("-f", "--format", choices=["csv", "txt"], nargs=1, default="txt",\
                        help="Format of the scraped ouput. Defaults to textfile.")
    parser.add_argument("-c", "--check", nargs=1, help="URL of English site to be checked.")

    # Retrieve user input
    args = parser.parse_args()
    if args.check:
        check_english(args.check)
    scrape_webpage(args.url, args.language, args.format)
    