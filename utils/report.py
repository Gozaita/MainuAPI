# -*- coding: utf-8 -*-
from utils import config
import os
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
        logger.debug("Se ha añadido el reporte")
        return True
    except Exception:
        logger.exception("No se ha podido escribir el report")
        return None


def get_reports():
    try:
        reports = []
        for file in os.listdir(REPORT_PATH):
            if file.endswith('.txt'):
                f = open(REPORT_PATH + file, 'r')
                contenido = f.read()
                rep = {'nombre': file[:-4],
                       'contenido': contenido}
                reports.append(rep)
        return reports
    except Exception:
        logger.exception("No se ha podido escribir el report")
        return None


def update_rep(rep):
    try:
        os.rename(REPORT_PATH + rep + '.txt', REPORT_PATH + rep + '.old')
        logger.debug("Visibilidad actualizada")
    except Exception:
        logger.exception("No se ha podido escribir el report")
        return None
