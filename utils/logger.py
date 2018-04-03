# -*- coding: utf-8 -*-
from time import localtime, strftime
from logging import FileHandler
from utils import config
import os
import logging


def get_handler():
    handler = FileHandler(filename=LOG_PATH,
                          encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s]: %(levelname)s - ' +
                                  '%(module)s - ' +
                                  '%(funcName)s - %(message)s')
    handler.setFormatter(formatter)
    return handler


LOG_PATH = config.get('PATH', 'root') + config.get('PATH', 'log')

try:
    log = open(LOG_PATH, 'a')
except FileNotFoundError:
    if not os.path.exists(os.path.dirname(LOG_PATH)):
        os.makedirs(os.path.dirname(LOG_PATH))
    log = open(LOG_PATH, 'w')


log.write("##############################################\n")
log.write("MainU -- mainu.eus -- %s\n"
          % strftime("%Y-%m-%d %H:%M:%S", localtime()))
log.write("API REST\n")
log.write("##############################################\n")
log.close()

logging.basicConfig(level=logging.DEBUG,
                    handlers=[get_handler()])

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
