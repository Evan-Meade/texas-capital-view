'''
Main script for scraping journals from the Texas House of
Representatives website.

'''

import re
import os
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import configparser


class HouseScraper:
    def __init__(self):
        print('Initializing HouseScraper...')
        self.BASE_URL = 'https://journals.house.texas.gov'
        self.QUERY_URL = 'https://journals.house.texas.gov/hjrnl/home.htm'
        self.MIN_YEAR = 82
        self.url_list = pd.DataFrame(columns=['url', 'download_path'], dtype='string')
        self.url_list.index.name = 'session'

        config = configparser.ConfigParser()
        config.read(os.path.expanduser('~/.texas-capital-view.ini'))
        self.base_dir = config['default']['base_dir']
        self.chrome_driver_dir = config['default']['chrome_driver_dir']
        self.options = Options()
        self.options.headless = True

        self.driver = webdriver.Chrome(options=self.options, executable_path=self.chrome_driver_dir)

        if os.path.isfile(os.path.join(self.base_dir, 'data', 'sessions.csv')):
            print('Loading sessions list...')
            self.url_list = pd.read_csv(os.path.join(self.base_dir, 'data', 'sessions.csv'), index_col='session')
            print('Loading complete.')
        
        print('Initialization complete.')

    def query_sessions(self):
        print('Querying session list...')
        self.driver.get(self.QUERY_URL)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        menu = soup.find('select')
        sessions = menu.find_all('option')

        session_regex = r'(\d{2}[A-Z])|(\d{3})'
        for s in sessions:
            print(s['value'])
            match = re.search(session_regex, s['value'])
            if match:
                year = int(match.group()[:2])
                if year >= self.MIN_YEAR:
                    self.url_list.loc[match.group(), 'url'] = self.BASE_URL + s['value']
        
        print('Done querying session list.')
        print(self.url_list)

        print('Writing session list...')
        data_dir = os.path.join(self.base_dir, 'data')
        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)
        self.url_list.to_csv(os.path.join(data_dir, 'sessions.csv'))
        print('Done writing session list.')
    
    def grab_journal(self, session):
        if self.url_list.shape[0] == 0:
            self.query_sessions()
