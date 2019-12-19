import re, os
from textblob import TextBlob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import StaleElementReferenceException


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


def yank_rel_hrefs(url, anchors):
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
        elif href.find("http"): 
            continue # Avoid external links
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
        if not re.search(r"^[\\\[\"\'\/]", text[line]):
            yield line


def detect_lang(text):
    """
    Uses Google Translate API to detect language
    """
    # Track frequencies of each language
    lang_freqs = dict()
    try:
        for line in text.split(","):
            blob = TextBlob(line)
            lang = blob.detect_language()
            lang_freqs[lang] = lang_freqs.get(lang, 0) + 1 # + 1; set lang if not there
    except:
        print("Failed to connect to Google Translate and detect language.")
        print("WARNING: Consider checking Internet connection.")
        return "Unknown"
    
    # Settle on the most frequent language
    lang = ""
    for k, v in lang_freqs.items():
        highest = 0
        if v > highest:
            highest = v
            lang = k

    return lang