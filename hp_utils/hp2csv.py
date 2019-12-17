#!usr/bin/env/python3
import os, sys, requests, csv, lxml, re
from bs4 import BeautifulSoup


def pull_hrefs(li_list):
    """pulls hrefs out of anchors in <li> list"""
    for li in li_list:
        a = li.find("a")
        yield a["href"]


def scrape2csv(url, link, directory):
    """Appends link to url and extracts html soup
    to output as csv into designated directory"""
    csv_title = link.split(".")[0]
    if csv_title.find("/") > -1:
        csv_title = csv_title.replace("/", "_")

    # Concatenate correctly with slash in between
    page_link = url + "/" + link
    r = requests.get(page_link)
    soup = BeautifulSoup(r.content, 'lxml', from_encoding="utf-8")
    text = soup.get_text(separator=",")

    # To convert into iterable
    text = text.split(",")

    # Regex for lines starting with special chars
    # all of which are set to empty strings to be filtered out later
    for line in range(len(text)):
        text[line] = text[line].strip() # Clean off empty space
        if re.search(r"^[\[\"\'\/]", text[line]):
            text[line] = "" 

    text = [ line for line in text if line != "" ] # Filter out empty lines
    
    # Path for saving the csv
    path = os.path.join(directory, csv_title) + ".csv"

    with open(path, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = [u"日本語", u"英語"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Title of file
        writer.writerow({fieldnames[0]: csv_title.upper(), fieldnames[1]: ""})
        writer.writeheader()
        for line in text:
            # writer.writerow({fieldnames[0]: "", fieldnames[1]: ""}) # Add empty line for better viewing
            writer.writerow({fieldnames[0]: line, fieldnames[1]: ""})
    
    print(f"Scraped {csv_title} to {path}")


def main():
    """This script parses a url and outputs its text to a csv"""
    if len(sys.argv) < 2:
        print("USAGE: python hp2csv.py <URL>")
        sys.exit(-1)

    url = sys.argv[1]
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    nav_list_items = soup.find_all("li", attrs={"class":"c-center"})
    links = pull_hrefs(nav_list_items)

    # Setting directory and folder for the csv
    dir_ = os.getenv("SCRAPE_PATH")
    folder_path = os.path.join(dir_, "hp2csv")
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)

    for link in links:
        scrape2csv(url, link, directory=folder_path)

    print(f"Finished scraping {url}")    
    sys.exit(0)


if __name__ == "__main__":
    main()