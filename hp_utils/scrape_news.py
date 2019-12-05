import os, sys, requests, lxml 
from bs4 import BeautifulSoup


def main():
    if len(sys.argv) < 2:
        print("USAGE: python scrape_news.py <URL>")
        sys.exit(-1)

    url = sys.argv[1]
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    li_list = soup.find_all("li", {"class": "c-center"})
    news_href = ""

    # Sift through nav <li>s 
    for li in li_list:
        a = li.find("a")
        if a["href"].find("news/index.html") > - 1:
            news_href = a["href"]
            break

    # Go to News page 
    news_res = requests.get(url + "/" + news_href)
    news_soup = BeautifulSoup(news_res.content, "lxml")

    # Get the button links
    anchors = news_soup.find_all("a", attrs={"class": "syousai"})
    href_list = [ anchor["href"] for anchor in anchors ]
    
    # Parse href link
    for i in range(len(href_list)):
        h_split = href_list[i].split("/")
        last = len(h_split) - 1
        href_list[i] = h_split[last-1] + "/" + h_split[last]
    
    folder = os.path.join(os.getenv("SCRAPE_PATH"), "hp2csv")
    filename = "news_index_items.txt"
    with open(os.path.join(folder, filename), "w", encoding="utf-8") as f:
        for h in href_list:
            print(f"Generating txtfile for {h}")
            res = requests.get(url + "/" + h)
            bs = BeautifulSoup(res.content, "lxml", from_encoding="utf-8")
            lines = bs.get_text(separator=",")
            lines = lines.split(",")
            lines = [ line.strip() for line in lines if line != "" ]
            f.writelines(lines)
            f.write("-------------------")
    
    print(f"News scraped. Check {folder} for files.")
    sys.exit(0)    


if __name__ == "__main__":
    main()

