import requests
from bs4 import BeautifulSoup
from uuid import uuid4
from txcapital import db


HOUSE_BASE_URL = 'https://house.texas.gov'
HOUSE_MEMBER_URL = f'{HOUSE_BASE_URL}/members/'


class HouseMemberScraper:
    def __init__(self):
        pass
    
    def get_member_list(self):
        page = requests.get(HOUSE_MEMBER_URL)
        soup = BeautifulSoup(page.content, 'html.parser')

        session = int(soup.find('div', id='session').find('span').text)

        member_divs = soup.find_all('td', class_='members-img-center')

        for div in member_divs:
            id_num = uuid4().hex

            member_name = div.find('strong').text.strip()
            split_name = member_name.split()
            first_name = split_name[2]
            last_name = split_name[1][:-1]
            middle_name = split_name[3] if len(split_name) > 3 else 'N/A'
            full_name = f'{first_name} {middle_name} {last_name}' if middle_name != 'N/A' else f'{first_name} {last_name}'

            district = int(div.text.strip().split()[1][:-4])

            

            url_path = div.find('a')['href']
            member_url = f'{HOUSE_BASE_URL}{url_path}'

            member = {
                '_id': id_num,
                'position': {
                    'current': {
                        'chamber': 'House',
                        'district': district,
                        'session': session
                    }
                },
                'name': {
                    'full': full_name,
                    'first': first_name,
                    'middle': middle_name,
                    'last': last_name
                },
                'member_url': member_url
            }

            self.update_member(member)
    
    def update_member(self, member):
        full_name = member['name']['full']
        existing_member = db.house_member.find_one({'name.full': full_name})

        if not existing_member:
            print(f'Inserting member {full_name}...')
            db.house_member.insert_one(member)
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
            db.house_member.update_one({'name.full': full_name},
                {'$set': {'position': existing_member['position'],
                    'member_url': existing_member['member_url']}})
                    