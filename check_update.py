import os
import sys
import ssl
import time
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

PWD = './'
CHROME_DRIVER_PATH = PWD + 'chromedriver'
UBLOCK_PATH = PWD + 'extension_1_26_0_0.crx'
BOOK_DATA_DIR = PWD + 'book_data/'

class Book:
    def __init__(self, name, url):
        self._name = name
        self._url = url
        self._book_data = BOOK_DATA_DIR + url.replace('/', '_')
        self._old_chapter_num = None
        self._new_chapter_num = None


    def check_update(self):
        self._get_old_chapter_num()         
        self._get_new_chapter_num()
        if self._old_chapter_num < self._new_chapter_num:
            self._update_book_data()
            return True
        return False


    def _get_new_chapter_num(self):
        response = urllib.request.urlopen(self.url)
        text = response.read().decode('utf-8', errors='ignore')
        self._new_chapter_num = len(text.split('<li><a href=')) - 1


    def _get_old_chapter_num(self):
        self._old_chapter_num = 0
        if os.path.isfile(self.book_data):
            f = open(self.book_data, 'r')
            self._old_chapter_num = int(f.read())
            f.close()


    def _update_book_data(self):
        f = open(self.book_data, 'w')
        f.write(str(self._new_chapter_num))
        f.close()

    @property
    def url(self):
        return self._url

    @property
    def name(self):
        return self._name

    @property
    def book_data(self):
        return self._book_data

class ChromeDriver:
    def __init__(self, url, ublock=True):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_extension(UBLOCK_PATH)
        self.driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=chrome_options)
        self.driver.maximize_window()
        time.sleep(3)
        self.driver.get(url)

    def new_tab(self, url):
        self.driver.execute_script("window.open();")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get(url)

    def close_all_tab(self):
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            self.driver.close()

class TextColor:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def use_default_ssl_context():
    ssl._create_default_https_context = ssl._create_unverified_context


if __name__ == '__main__':
    use_default_ssl_context()
    books = [
        Book('<BookName>', '<BookUrl'),
    ]

    has_update = False
    driver = None
    for book in books:
        if book.check_update():
            print("{}. {} {}已更{}".format(books.index(book)+1, book.name, TextColor.OKGREEN, TextColor.ENDC))
            if not has_update:
                driver = ChromeDriver(book.url)
                has_update = True
            else:
                driver.new_tab(book.url)
        else:
            print("{}. {} {}未更{}".format(books.index(book)+1, book.name, TextColor.WARNING, TextColor.ENDC))

    time.sleep(1)
    print("輸入設定要為未更新的書")
    book_to_set_not_update = input()
    if book_to_set_not_update != '':
        book_to_set_not_update = book_to_set_not_update.split(' ')
        for book in book_to_set_not_update:
            if book.isnumeric():
                print("設定編號{} 的書為未更新".format(int(book)))
                os.remove(books[int(book)-1].book_data)
            else:
                print("沒有編號為 {} 的書".format(book))

    if has_update:
        driver.close_all_tab()
