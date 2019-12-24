import re, os
from textblob import TextBlob
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import StaleElementReferenceException

    
class InvalidURLError(Exception):
    pass


def verify_url(url):
    """
    Uses re module and built-in str methods to check whether URL is valid
    """
    is_valid = False
    if re.search(r"^https?://www\.", url) and re.search(r".*\.\w{2,3}/?$", url):
        is_valid = True

    return is_valid


def correct_url(url):
    """
    Returns a verified URL after appending a forward slash
    """
    if not verify_url(url):
        raise InvalidURLError
    if not url.endswith("/"):
        url += "/"
    return url


def verify_dir(dir_):
    """
    Checks whether dir is an absolute path.
    Makes dir if not yet existing.
    """
    is_valid = False

    # Check if absolute without a file extension
    if os.path.isabs(dir_) and not os.path.splitext(dir_)[1]:
        is_valid = True
    if not os.path.exists(dir_):
        os.mkdir(dir_)
    
    return is_valid


def yank_hrefs_via_driver(root, url):
    """
    Uses Selenium à la Chrome to parse dynamic webpage for relative links
    """
    from time import sleep
    print(f"Using Chrome Webdriver to scrape {url}")

    # TODO
    # Check path for Chrome driver before running up to here

    # Edit url for relative link parsing
    if not root.endswith("/"):
        root += "/"

    # Set up driver
    options = Options()
    options.add_argument("--headless") # Run headless

    # Configuration to avoid other possible, client-side bugs
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.binary_location = os.getenv("CHROME_DRIVER")

    # Init driver with config
    try:
        browser = webdriver.Chrome(options=options)
    except:
        print("Could not find chromedriver executable. Set to PATH and try again.")
        return None

    # Go to page
    browser.get(url)

    # Wait for content to load
    sleep(3)

    # Get all anchors in the dynamic page
    # yield their respective href if relative
    anchors = browser.find_elements_by_tag_name("a")
    for a in anchors:
        href = a.get_attribute("href")
        # If full links are returned, take only the suffix
        if href.find(root) == 0:
            end = len(root)
            yield href[end:]

    # Close driver process
    browser.quit()


def yank_hrefs(root, url, anchors):
    """
    Returns a set of hrefs from a list of anchors
    """
    href_set = set()
    for anchor in anchors:
        href = anchor["href"]
        if href.find(".") == -1:
            # Faulty url found;
            # pass url to selenium driver for yanking
            try:
                for x in yank_hrefs_via_driver(root, url):
                    href_set.add(x)
                break
            except AttributeError:
                # Error in web driver
                return None
        elif href.find("http"): 
            continue # Avoid external links
        else:
            href_set.add(anchor["href"])   

    return href_set


def clean_text(text):
    """
    Returns the input text after cleaning for extraneous spaces and symbols
    """
    # Regex for lines starting with special chars
    # all of which are set to empty strings to be filtered out later
    for line in text.split(","):
        line = line.strip() # Clean off empty space
        if not re.search(r"^[\\\[\"\'\/]", line):
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
    highest = 0
    for k, v in lang_freqs.items():
        if v > highest:
            highest = v
            lang = k

    return lang