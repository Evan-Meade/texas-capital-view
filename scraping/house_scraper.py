'''
Main script for scraping journals from the Texas House of
Representatives website.

'''

import re
import requests
from bs4 import BeautifulSoup


class HouseScraper:
    def __init__(self):
        self.BASE_URL = 'https://journals.house.texas.gov/hjrnl'
        self.MIN_YEAR = 82

    def query_years(self):
        page = requests.get(self.BASE_URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        menu = soup.find('select')

        session_regex = r'(\d{2}[A-Z])|(\d{3})'
        
