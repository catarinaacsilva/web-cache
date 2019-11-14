# coding: utf-8


__author__ = 'Catarina Silva'
__version__ = '0.0.2'
__email__ = 'c.alexandracorreia@ua.pt'
__status__ = 'Development'


import os
import bz2
import time
import string
import pickle
import logging
import requests
import threading

from bs4 import BeautifulSoup as bs

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


USER_AGENT_LINUX_FIREFOX55 = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'
USER_AGENT_LINUX_CHROME = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/78.0.3904.70 Chrome/78.0.3904.70 Safari/537.36'


logger = logging.getLogger('WC')


# legacy code...
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


# new code to deal with name creation
def format_filename(s: str):
    """Take a string and return a valid filename constructed from the string.
Uses a whitelist approach: any characters not present in valid_chars are
removed. Also spaces are replaced with underscores.
 
Note: this method may produce invalid filenames such as ``, `.` or `..`
When I use this method I prepend a date string like '2009_01_15_19_46_32_'
and append a file extension like '.txt', so I avoid the potential of using
an invalid filename.
 
"""
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    filename = filename.replace(' ','_') # I don't like spaces in filenames.
    return filename


def get_request(url: str, timeout: int, headers={}):
    try:
        response = requests.get(url, headers = header, verify=False, allow_redirects=True, timeout = timeout)
        return response
    except Exception as e:
        logger.warning(e)
        return None


def get_header(url: str, timeout: int, headers={}):
    try:
        headers = requests.head(url, headers = header, verify=False, allow_redirects=True, timeout = timeout)
    except Exception as e:
        logger.warning(e)
        return None


# HTML meta redirect
def meta_redirect(content):
    soup  = bs(content, features='html.parser')
    result_upper = soup.select_one('meta[HTTP-EQUIV="REFRESH"]')
    result_lower = soup.select_one('meta[http-equiv="refresh"]')
    
    if result_upper:
        wait,text=result_upper["content"].split(";")
        if text.strip().startswith("url="):
            url=text[5:]
            return url
    
    if result_lower:
        wait,text=result_lower["content"].split(";")
        if text.strip().startswith("url="):
            url=text[5:]
            return url
    
    return None

    
def fetch_raw_html(url: str, timeout: int, user_agent=USER_AGENT_LINUX_CHROME):
    headers = {'User-agent': user_agent}
    #reply = requests.get(url, headers = header, verify=False, allow_redirects=True)
    reply = get_request(url, timeout)

    if reply is not None and reply.status_code == 200:
        redirect_url = meta_redirect(reply.text)
        if redirect_url:
            return fetch_raw_html(redirect_url, user_agent)
        else:
            return reply.text
    else:
        return None


def fetch_rendered_html(url: str, driver: webdriver):
    driver.get(url)
    #html_rendered = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    html_rendered = driver.page_source
    redirect_url = meta_redirect(html_rendered)
    if redirect_url:
        return fetch_rendered_html(redirect_url, driver)
    else:
        return html_rendered


def load_url(url: str, filename: str, driver: webdriver, timeout: int):
    logger.debug('Load %s and store it on %s', url, file_name)
    logger.debug('Filename = %s', file_name)
    try:
        logger.debug('GET RAW HTML...')
        html_raw = fetch_raw_html(url, timeout)
        logger.debug('GET Rendered HTML...')
        html_rendered = fetch_rendered_html(url, driver)
        logger.debug('Generate HTML screenshot...')
        element = driver.find_element_by_tag_name('body')
        img = element.screenshot_as_png
        #with open("test2.png", "wb") as file:
        #    file.write(element_png)
        #driver.save_screenshot('/tmp/screenshot.png')
        #logger.debug('Load screenshot...')
        #with open('/tmp/screenshot.png', 'rb') as f:
        #    img = f.read()
        #os.remove('/tmp/screenshot.png')
        data = {'html_raw': html_raw, 'html_rendered': html_rendered, 'img': img}
        with bz2.BZ2File(filename, 'w') as f:
            pickle.dump(data, f)
        return data
    except Exception as e:
        logger.warning(e)
        if os.path.isfile(filename):
            os.remove(filename)
        return None


def load_compressed_file(filename: str):
    logger.debug('Load compressed file %s', filename)
    with bz2.BZ2File(filename, 'r') as f:
        data = pickle.load(f)
    return data


class WebCache(object):
    def __init__(self, path='/tmp/webcache', ttl=24*3600, timeout=10):
        self.path = path
        self.ttl = ttl
        self.timeout = timeout
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        self.lock = threading.Lock()
    
    def get(self, url: str, refresh=False):
        filename = '{}/{}.bz2'.format(self.path, format_filename(url))
        
        with self.lock:
            if refresh:
                html = load_url(url, filename, self.driver, self.timeout)
            elif os.path.exists(file_name):
                creation_time = os.path.getmtime(filename)
                alive_time = time.time() - creation_time
                if alive_time > self.ttl:
                    html = load_url(url, filename, self.driver, self.timeout)
                else:
                    html = load_compressed_file(filename)
            else:
                html = load_url(url, filename, self.driver, self.timeout)
        return html

    def __del__(self):
        self.driver.stop_client()
        self.driver.close()
