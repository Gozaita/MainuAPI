# -*- coding: utf-8 -*-
from configparser import ConfigParser
from ast import literal_eval
from os.path import dirname
import logging

ROOT = dirname(dirname(__file__)) + '/'

config = ConfigParser()
config.read(ROOT + 'utils/.config')
config.set('PATH', 'root', ROOT)

#############################################
# Explicación de errores 400
#############################################

BAD_ACTION = ('Se debe pasar como query-string una acción (action), que puede '
              'ser \'visible\' o \'delete\'. Por ejemplo: '
              '/update_val/bocadillos/14?action=visible.')

BAD_TYPE = ('Comprueba que el <type> indicado es válido (bocadillos, menu, '
            'otros).')

BAD_ID = ('Comprueba que el <id> indicado existe.')

BAD_TYPE_ID = ('Comprueba que el <type> indicado es válido (bocadillos, menu, '
               'otros) y que, en caso de haber pasado un <id>, éste también '
               'lo es.')

#############################################

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
