# Honyaku.py
Need to translate a website but not sure if you will (or want to) catch every word via copy-paste?<br>
Honyaku can help!

## Usage
```
python honyaku.py URL -d DIRECTORY -f FORMAT {csv, txt} -L LANGUAGE
```
This will save all the text from every webpage internal to the initially input URL<br>
as either a text file or CSV (default).
Don't worry about duplicates! Honyaku is smart enough to avoid copying the same page twice.
Even if you're not sure what language you're translating, Honyaku will ask Google Translate to guess!
<br>
<br>
OR to *check* your English translation, try the following command!
```
python honyaku.py URL -c 
```

## Note
If you didn't know, Honyaku uses scraping libraries for its magic! <br>
While BeautifulSoup is its first choice, if in scraping for links it finds something that doesn't resemble a URL,<br>
Honyaku will then summon Selenium to parse what's probably a dynamic webpage.<br>
At that time Honyaku will prompt you for a path to a Chrome Webdriver executable,
which may be downloaded here: https://chromedriver.chromium.org/downloads

If your refuse to download it, that's fine--Honyaku will do as much work as it can without the driver.
