import queue
from .util import correct_url

class ScrapeQueue():
    """
    Queue of URLs internal to the initial root 
    that are to be scrapped
    """
    def __init__(self, root):
        root = correct_url(root) # Verify and append "/"
        url_memo = {root} # Set instance to ensure uniqueness

        self.__root = root
        self.__url_memo = url_memo
        self.__queue = self.__init_queue(url_memo.copy())

    def __len__(self):
        return len(self.__queue.queue)

    def __init_queue(self, url_set):
        """Instantiates queue"""
        q = queue.Queue()
        for url in url_set:
            q.put(url)            
        return q

    def dequeue(self):
        """Pops url off queue"""
        if self.__queue.empty():
            return None
        return self.__queue.get()

    def enqueue(self, url):
        """Adds url to queue if new and internal to roo"""
        # Found an external link
        if not url.find(self.__root) == 0 and url.startswith("http"):
            print(f"Skipped enqueue of external link: {url}")
            return None
        # Append root to relative url
        if not url.find(self.__root) == 0 and \
            url.endswith(".html") or url.endswith(".aspx"):
            url = self.__root[:] + url            
        # Verify whether scraped already    
        if url not in self.__url_memo:
                self.__url_memo.add(url)
                self.__queue.put(url)