'''
Main script for scraping journals from the Texas House of
Representatives website.

'''

import re
import pandas as pd
import requests
from bs4 import BeautifulSoup


class HouseScraper:
    def __init__(self):
        self.BASE_URL = 'https://journals.house.texas.gov/hjrnl'
        self.QUERY_URL = 'https://journals.house.texas.gov/hjrnl/home.htm'
        self.MIN_YEAR = 82
        self.url_list = pd.DataFrame(columns=['url', 'download_path'])

    def query_years(self):
        page = requests.get(self.QUERY_URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        menu = soup.find('select')
        sessions = menu.find_all('option')

        session_regex = r'(\d{2}[A-Z])|(\d{3})'
        for s in sessions:
            match = re.search(session_regex, s.value)
            if match:
                year = int(match.group[:2])
                if year >= self.MIN_YEAR:
                    self.url_list[match.group()] = [s.value, '']
        
        print(self.url_list)


hs = HouseScraper()
hs.query_years()
        
