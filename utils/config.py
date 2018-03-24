from configparser import ConfigParser
from ast import literal_eval
from os.path import dirname
import logging

ROOT = dirname(dirname(__file__)) + '/'

print('root:')
print(ROOT)

config = ConfigParser()
config.read(ROOT + 'utils/.config')
config.set('PATH', 'root', ROOT)

logger = logging.getLogger(__name__)


def get(section, name):
    return config.get(section, name)


def get_database():
    user = config.get('DATABASE', 'user')
    pswd = config.get('DATABASE', 'password')
    host = config.get('DATABASE', 'host')
    schm = config.get('DATABASE', 'schema')
    return user, pswd, host, schm


def get_httpauth():
    usrs = literal_eval(config.get('HTTPAUTH', 'users'))
    return usrs
