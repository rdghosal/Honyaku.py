import os, sys, requests, lxml, html5lib
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep

def main():
    if len(sys.argv) < 2:
        print("USAGE: python scrape_news.py <URL>")
        sys.exit(-1)

    url = sys.argv[1]

    # Open page
    browser = webdriver.Chrome(os.getenv("CHROME"))
    browser.get(url)

    # Find target tab, click,
    # and grab all anchor elements there
    browser.find_element_by_xpath("//a[text()='News']").click()
    sleep(3)
    anchors = browser.find_elements_by_xpath("//a[@class='syousai']")
    
    tar_paths = ["//h4[@class=' c-small_headline']", "//p[@class=' c-body']"]

    text = ""
    pos = 50
    for i in range(len(anchors)):
        sleep(5)
        anchors[i].click()
        headlines = browser.find_elements_by_xpath(tar_paths[0])
        for h in headlines:
            text += h.text
            text += "\n"
        text += "===\n"
        body = browser.find_element_by_xpath(tar_paths[1])
        text += body.text
        "\n**************\n"
        browser.back()
        browser.execute_script(f"window.scrollTo({pos})")
        sleep(2)
    
    dest = os.path.join(os.getenv("SCRAPE_PATH"), "news_scraped.txt")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Scraping complete! Check {os.getenv('SCRAPE_PATH')}")    

        


    # news_href = ""
    
    # # Sift through nav <li>s 
    # for li in li_list:
    #     a = li.find("a")
    #     if a["href"].find("news/index.html") > - 1:
    #         news_href = a["href"]
    #         break

    # # Go to News page 
    # news_res = requests.get(url + "/" + news_href)
    # news_soup = BeautifulSoup(news_res.content, "html5lib")
    # print(news_soup)

    # # Get the button links
    # anchors = news_soup.find_all("a", attrs={"class": "syousai"})
    # href_list = [ anchor["href"] for anchor in anchors ]
    
    # # Parse href link
    # for i in range(len(href_list)):
    #     h_split = href_list[i].split("/")
    #     last = len(h_split) - 1
    #     href_list[i] = h_split[last-1] + "/" + h_split[last]
    
    # folder = os.path.join(os.getenv("SCRAPE_PATH"), "hp2csv")
    # filename = "news_index_items.txt"
    # with open(os.path.join(folder, filename), "w", encoding="utf-8") as f:
    #     for h in href_list:
    #         print(f"Generating txtfile for {h}")
    #         res = requests.get(url + "/" + h)
    #         bs = BeautifulSoup(res.content, "lxml", from_encoding="utf-8")
    #         lines = bs.get_text(separator=",")
    #         lines = lines.split(",")
    #         lines = [ line.strip() for line in lines if line != "" ]
    #         f.writelines(lines)
    #         f.write("\n")
    #         f.write("-------------------")
    #         f.write("\n")
    
    # print(f"News scraped. Check {folder} for files.")
    sys.exit(0)    


if __name__ == "__main__":
    main()

