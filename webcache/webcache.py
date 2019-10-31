# coding: utf-8


__author__ = 'Catarina Silva'
__version__ = '0.0.2'
__email__ = 'c.alexandracorreia@ua.pt'
__status__ = 'Development'


import os
import bz2
import time
import pickle
import logging
import requests
import threading

from selenium import webdriver
from selenium.webdriver.firefox.options import Options


logger = logging.getLogger('WC')


def fnv1a_32(string: str, seed=0):
    """
    Returns: The FNV-1a (alternate) hash of a given string
    """
    #Constants
    FNV_prime = 16777619
    offset_basis = 2166136261

    #FNV-1a Hash Function
    hash = offset_basis + seed
    for char in string:
        hash = hash ^ ord(char)
        hash = hash * FNV_prime
    return hash


def load_url(url: str, file_name: str, driver: webdriver):
    logger.debug('Load %s and store it on %s', url, file_name)
    logger.debug('Filename = %s', file_name)
    try:
        logger.debug('GET RAW HTML...')
        user_agent = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'}
        reply = requests.get(url, headers = user_agent)
        html_raw = reply.text
        logger.debug('GET Rendered HTML...')
        driver.get(url)
        html_rendered = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
        logger.debug('Generate HTML screenshot...')
        driver.save_screenshot('/tmp/screenshot.png')
        logger.debug('Load screenshot...')
        with open('/tmp/screenshot.png', 'rb') as f:
            img = f.read()
        os.remove('/tmp/screenshot.png')
        data = {'html_raw': html_raw, 'html_rendered': html_rendered, 'img': img}
        with bz2.BZ2File(file_name, 'w') as f:
            pickle.dump(data, f)
        return data
    except TimeoutException as ex:
        return None


def load_compressed_file(file_name: str):
    logger.debug('Load compressed file %s', file_name)
    with bz2.BZ2File(file_name, 'r') as f:
        data = pickle.load(f)
    return data


class WebCache(object):
    def __init__(self, path='/tmp/webcache', ttl=24*3600):
        self.path = path
        self.ttl = ttl
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.lock = threading.Lock()
    
    def get(self, url: str, refresh=False):
        file_name = '{}/{}.bz2'.format(self.path, hex(fnv1a_32(url)))
        
        with self.lock:
            if refresh:
                html = load_url(url, self.path, self.driver)
            elif os.path.exists(file_name):
                creation_time = os.path.getmtime(file_name)
                alive_time = time.time() - creation_time
                if alive_time > self.ttl:
                    html = load_url(url, file_name, self.driver)
                else:
                    html = load_compressed_file(file_name)
            else:
                html = load_url(url, file_name, self.driver)
        return html

    def __del__(self):
        self.driver.stop_client()
        self.driver.close()
