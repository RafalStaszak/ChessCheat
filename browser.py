from selenium import webdriver
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException


class Browser:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--user-data-dir=/home/rafal/.config/google-chrome")
        self.driver = webdriver.Chrome('files/chromedriver', options=options)
        self._setup()

    def open(self, webpage='https://google.com'):
        self.driver.get(webpage)

    def get_data(self, url):
        data = list()
        if 'chess.com' in url:
            try:
                html = self.driver.find_element_by_class_name('vertical-move-list-component').get_attribute('outerHTML')
                data.append(html)
            except (NoSuchElementException, StaleElementReferenceException):
                pass
            try:
                html = self.driver.find_element_by_class_name('computer-move-list').get_attribute('outerHTML')
                data.append(html)
            except (NoSuchElementException, StaleElementReferenceException):
                pass

        if 'lichess.org':
            try:
                html = self.driver.find_element_by_class_name('moves').get_attribute('outerHTML')
                data.append(html)
            except (NoSuchElementException, StaleElementReferenceException):
                pass
        return data

    @property
    def url(self):
        return self.driver.current_url

    def _setup(self):
        # self._browser.switch_to.alert.dismiss()
        pass

    def close(self):
        self.__del__()

    def __del__(self):
        self.driver.close()
