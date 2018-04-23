# -*- coding: utf-8 -*-
from utils import config
import logging
import time

REPORT_PATH = config.get('PATH', 'root') + config.get('PATH', 'reports')

logger = logging.getLogger(__name__)


def write_report(report):
    try:
        timestamp = time.strftime("%Y-%m-%d--%H-%M-%S")
        nombre = timestamp
        f = open(REPORT_PATH + nombre + '.txt', 'w')
        f.write(report)
        f.close()
        return True
    except Exception:
        logger.exception("No se ha podido escribir el report")
        return None
