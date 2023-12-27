import requests
from bs4 import BeautifulSoup
import time
import logging
import re

class Scraper:
    def __init__(self):
        self.headers_list = []
        self.proxy_list = []
        self.logger = logging.getLogger(__name__)
        self.rate_limit = 5

    def fetch(self, url, retries=3):
        for i in range(retries):
            try:
                # Randomize the headers to avoid getting blocked by the server
                response = requests.get(url)
                if response.status_code == 200:
                    return response.text
                else:
                    self.logger.error(f"Error fetching {url}: {response.status_code}")
            # If there is error let's wait for a while before trying again (scuffed rate limiting)
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error fetching {url}: {e}")
                if i < retries - 1:  # no need to wait on the last iteration
                    time.sleep(self.rate_limit)  # wait before retrying
        return None
    
    def find_urls(self, url, pattern: re.Pattern):
        response = self.fetch(url)
        if not response:
            return []
        soup = BeautifulSoup(response, 'html.parser')
        return [link['href'] for link in soup.find_all('a', href=pattern) if link['href']]
