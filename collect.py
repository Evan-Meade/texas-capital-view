from txcapital.collect import HouseMemberScraper, SenateMemberScraper

hms = HouseMemberScraper()
hms.get_member_list()

sms = SenateMemberScraper()
sms.get_member_list()
