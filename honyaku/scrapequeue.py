import queue

class ScrapeQueue():
    """Queue of unique URLs to be used for scraping"""
    def __init__(self, urls=set()):
        # Ensure that only a set is passed
        self.__url_memo = set(urls) if not isinstance(urls, set) else urls
        self.__queue = self._init_queue(self.__url_memo.copy())

    def __len__(self):
        return len(self.__queue.queue)

    def _init_queue(self, url_set):
        """Instantiates queue"""
        q = queue.Queue()
        for url in url_set:
            q.put(url)            
        return q

    def dequeue(self):
        """Pops url off queue"""
        return self.__queue.get()

    def enqueue(self, url):
        """Adds url to queue if new"""
        if url not in self.__url_memo:
            self.__url_memo.add(url)
            self.__queue.put(url)