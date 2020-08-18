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
        self.url_list = pd.DataFrame(columns=['title', 'url', 'download_path'], dtype='string')
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
            self.url_list = pd.read_csv(os.path.join(self.base_dir, 'data', 'sessions.csv'), index_col='session', dtype='string')
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
                    self.url_list.loc[match.group(), 'title'] = s.text
                    self.url_list.loc[match.group(), 'url'] = self.BASE_URL + s['value']
        
        print('Done querying session list.')
        print(self.url_list)

        print('Writing session list...')
        data_dir = os.path.join(self.base_dir, 'data')
        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)
        self.url_list.to_csv(os.path.join(data_dir, 'sessions.csv'))
        print('Done writing session list.')

        print('Done querying session list.')
    
    def query_journals(self, session):
        if self.url_list.shape[0] == 0:
            self.query_sessions()
        if session not in self.url_list.index.values:
            print(f'Invalid session code provided: {session}')
            return
        print(f'Grabbing session {session}...')
        
        journal_list = pd.DataFrame(columns=['url', 'download_path'])
        journal_list.index.name = 'journal'

        target_url = self.url_list.loc[session, 'url']
        self.driver.get(target_url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        table = soup.find('table', id='jrnlGrid')
        cells = table.find_all('td')

        print('Creating directory structure...')
        data_dir = os.path.join(self.base_dir, 'data')
        if not os.path.isdir(data_dir):
            os.mkdir(data_dir)
        house_dir = os.path.join(data_dir, 'house')
        if not os.path.isdir(house_dir):
            os.mkdir(house_dir)
        session_dir = os.path.join(house_dir, session)
        if not os.path.isdir(session_dir):
            os.mkdir(session_dir)
        self.url_list.loc[session, 'download_path'] = session_dir
        print('Done creating directory structure.')

        print('Pulling URLs from table...')
        for c in cells:
            if 'title' in c.attrs and 'html' in c['title'].lower():
                links = c.find_all('a')
                for l in links:
                    if 'htm' in l['href'].lower():
                        print(l['href'])
                        filename = os.path.basename(l['href'])
                        journal_list.loc[filename, 'url'] = self.BASE_URL + l['href']
        print('Done pulling URLs from table.')
        
        print('Writing journal list...')
        journal_list.to_csv(os.path.join(session_dir, f'{session}.csv'))
        print('Done writing journal list.')

        print(f'Done grabbing session {session}.')

hs = HouseScraper()
hs.query_journals('85R')
        
        
