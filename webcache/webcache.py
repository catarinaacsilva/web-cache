# coding: utf-8


__author__ = 'Catarina Silva'
__version__ = '0.0.1'
__email__ = 'c.alexandracorreia@ua.pt'
__status__ = 'Development'


import logging
import os
import time
import gzip
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


def load_url(url: str, path: str, driver: webdriver):
    logger.debug('Load %s and store it on %s', url, path)
    file_name = '{}/{}.gz'.format(path, hex(fnv1a_32(url)))
    logger.debug('Filename = %s', file_name)
    driver.get(url)
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    logger.debug('HTML = %s', html)
    with gzip.open(file_name, 'wt') as f:
        f.write(html)
    return html


class WebCache(object):
    def __init__(self, path='/tmp/webcache', ttl=24*3600):
        self.path = path
        self.ttl = ttl
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        
    def get(self, url: str, refresh=False):
        file_name = '{}/{}.gz'.format(self.path, hex(fnv1a_32(url)))
        if os.path.exists(file_name):
            creation_time = os.path.getmtime(file_name)
            alive_time = time.time()-creation_time
            if alive_time > self.ttl:
                html = load_url(url, self.path, self.driver)
            else:
                html = None
                with gzip.open(file_name, 'rt') as f:
                    html = f.read()
        else:
            html = load_url(url, self.path, self.driver)

        return html

    def __del__(self):
        self.driver.stop_client()
        self.driver.close()


    