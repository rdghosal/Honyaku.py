from bs4 import BeautifulSoup
import html5lib
import requests
import sys

def main():
    if len(sys.argv) < 2:
        print("Need more args")

    url = sys.argv[1]
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html5lib")

    links = soup.find_all("a", attrs={"class": "syousai"})
    for l in links:
        print(l)
        print(f"clicking {l.href}")
        res = requests.get(url + "/" + l["href"])
        print(res.content)
    
    print("finished")

if __name__ == "__main__": main()