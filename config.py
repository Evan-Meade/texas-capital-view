import os
import configparser


CONFIG_FILE = os.path.expanduser('~/.texas-capital-view.ini')


print('Make sure to run this script from the base directory of the repository!')

config = configparser.ConfigParser()

print('Locating base directory...')

chrome_dir = input('\nWhere is your ChromeDriver installed (for selenium)?\n')

print('\nCompiling configuration...')
config['default'] = {'base_dir': str(os.getcwd()), 'chrome_driver_dir': chrome_dir}

print('\nWriting configuration...')
with open(CONFIG_FILE, 'w') as cf:
    config.write(cf)
    cf.close()

print('Done!')