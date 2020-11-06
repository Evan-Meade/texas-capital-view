import requests
from bs4 import BeautifulSoup
from uuid import uuid4
from txcapital import db
import re


SENATE_BASE_URL = 'https://senate.texas.gov/'
SENATE_MEMBER_URL = f'{SENATE_BASE_URL}members.php'


class SenateMemberScraper:
    def __init__(self):
        pass

    def get_member_list(self):
        page = requests.get(SENATE_MEMBER_URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        page_title = soup.find('div', class_='pgtitle').text
        session = int(re.search('\d+', page_title).group())

        member_divs = soup.find_all('div', class_='mempicdiv')

        for div in member_divs:
            member = {}

            id_num = uuid4().hex
            member['_id'] = id_num

            full_name = div.find_all('a')[1].text
            split_name = full_name.split()
            first_name = split_name[0]
            last_name = split_name[-1]
            name = {
                'full': full_name,
                'first': first_name,
                'last': last_name
            }
            if len(split_name) > 2:
                middle_name = split_name[1:-1]
                if isinstance(middle_name, list):
                    middle_name = ' '.join(middle_name)
                name['middle'] = middle_name
            member['name'] = name

            district_text = div.find('span').text
            district = int(re.search('\d+', district_text).group())
            position = {
                'current': {
                    'chamber': 'Senate',
                    'district': district,
                    'session': session
                }
            }
            member['position'] = position

            url_path = div.find('a').get('href')
            member_url = f'{SENATE_BASE_URL}{url_path}'
            member['member_url'] = member_url

            self.update_member(member)
    
    def update_member(self, member):
        full_name = member['name']['full']
        existing_member = db.senate_member.find_one({'name.full': full_name})

        if not existing_member:
            print(f'Inserting member {full_name}...')
            db.senate_member.insert_one(member)
        else:
            if not existing_member['position']['current'] == member['position']['current']:
                if 'previous' not in existing_member['position']:
                    existing_member['position']['previous'] = [
                        existing_member['position']['current']
                    ]
                else:
                    existing_member['position']['previous'].append(existing_member['position']['current'])

                existing_member['position']['current'] = member['position']['current']

            existing_member['member_url'] = member['member_url']

            print(f'Updating member {full_name}...')
            db.senate_member.update_one({'name.full': full_name},
                {'$set': {'position': existing_member['position'],
                    'member_url': existing_member['member_url']}})
            