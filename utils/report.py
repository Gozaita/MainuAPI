# -*- coding: utf-8 -*-
from utils import config
import logging
import time

logger = logging.getLogger(__name__)


def escribir_ficehro(report):
    try:
        timestamp = time.strftime("%Y-%m-%d--%H-%M-%S")
        nombre = timestamp
        f = open(nombre+'.txt', 'w')
        f.write(report)
        f.close()
        return nombre
    except Exception:
        logger.exception("No se ha podido escribir el report")
        return None
