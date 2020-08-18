import os
import configparser


CONFIG_FILE = 'config.ini'


print('Make sure to run this script from the base directory of the repository!')

config = configparser.ConfigParser()

print('Writing base directory...')
config['default'] = {'base_dir': str(os.getcwd())}

with open(CONFIG_FILE, 'w') as cf:
    config.write(cf)
    cf.close()

print('Done!')