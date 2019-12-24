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
Thus, you'll need to have downloaded the **chromedriver matching your version of Google Chrome** to run Honyaku error-free.<br>
The chromedriver can be downloaded here: https://chromedriver.chromium.org/downloads

To see what file outputs look like, take a look at the `examples` folder!