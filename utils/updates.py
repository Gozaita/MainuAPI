# -*- coding: utf-8 -*-
from time import localtime, strftime
from utils import config
import logging
import json
import sys

logger = logging.getLogger(__name__)

PATH = config.get('PATH', 'root') + config.get('LAST_UPDATES', 'path')
MAIN = PATH + config.get('LAST_UPDATES', 'main')
BOCD = PATH + config.get('LAST_UPDATES', 'bocadillos')
PLAT = PATH + config.get('LAST_UPDATES', 'platos')
OTHS = PATH + config.get('LAST_UPDATES', 'otros')


def init():
    try:
        mainf = open(MAIN, 'r')
        logger.info("Se ha encontrado el fichero: %s"
                    % MAIN)
        bocdf = open(BOCD, 'r')
        logger.info("Se ha encontrado el fichero: %s"
                    % BOCD)
        platf = open(PLAT, 'r')
        logger.info("Se ha encontrado el fichero: %s"
                    % PLAT)
        othsf = open(OTHS, 'r')
        logger.info("Se ha encontrado el fichero: %s"
                    % OTHS)
    except FileNotFoundError:
        logger.error("No se ha podido acceder a uno o varios de los " +
                     "directorios de actualización")
        sys.exit(1)

    global main, bocd, plat, oths

    main = json.load(mainf)
    mainf.close()
    bocd = json.load(bocdf)
    bocdf.close()
    plat = json.load(platf)
    platf.close()
    oths = json.load(othsf)
    othsf.close()

    logger.info("El tamaño de main es %d" % len(main))
    logger.info("El tamaño de bocd es %d" % len(bocd))
    logger.info("El tamaño de plat es %d" % len(plat))
    logger.info("El tamaño de oths es %d" % len(oths))


def write(dict):
    if dict is main:
        path = MAIN
    if dict is bocd:
        path = BOCD
    if dict is plat:
        path = PLAT
    if dict is oths:
        path = OTHS
    try:
        file = open(path, 'w')
        json.dump(dict, file)
        file.close()
        return True
    except FileNotFoundError:
        logger.warning("No se puede acceder al directorio de " +
                       "actualización %s. No se realizará el " % path +
                       "volcado de datos")
        return False


def get_last_update(type, id=None):
    """
    Devuelve la última fecha de modificación de una lista de <type> o de un
    elemento concreto de la misma identificado por su <id>. Si el <type> no
    se encuentra entre los admitidos o no se encuentra el <id>, se devolverá
    un String vacío.
    """
    res = ''
    if id is None:
        if type == 'bocadillos' or type == 'menu' or type == 'otros':
            logger.debug("type: %s" % type)
            res = main.get(type, None)
        else:
            logger.warning("type: %s\n" % type +
                           "El tipo es inválido")
    else:
        if type == 'bocadillos':
            logger.debug("type: %s, id: %s" % (type, id))
            res = bocd.get(id, None)
        elif type == 'menu':
            logger.debug("type: %s, id: %s" % (type, id))
            res = plat.get(id, None)
        elif type == 'otros':
            logger.debug("type: %s, id: %s" % (type, id))
            res = oths.get(id, None)
        else:
            logger.warning("type: %s, id: %s\n" % (type, id) +
                           "El tipo es inválido")
    return res


def modify_last_update(type, id=None):
    """
    Actualiza la última fecha de modificación de una lista de <type> o de un
    elemento concreto de la misma identificado por su <id>. Si el <type> no
    se encuentra entre los admitidos, se devolverá un String vacío.
    """
    time = strftime("%Y-%m-%d %H:%M:%S", localtime())
    if id is None:
        if type == 'bocadillos' or type == 'menu' or type == 'otros':
            logger.debug("type: %s" % type)
            main[type] = time
            write(main)
        else:
            logger.warning("type: %s\n" % type +
                           "El tipo es inválido")
            return False
    else:
        if type == 'bocadillos':
            logger.debug("type: %s, id: %s" % (type, id))
            bocd[id] = time
            write(bocd)
        elif type == 'menu':
            logger.debug("type: %s, id: %s" % (type, id))
            plat[id] = time
            write(plat)
        elif type == 'otros':
            logger.debug("type: %s, id: %s" % (type, id))
            oths[id] = time
            write(oths)
        else:
            logger.warning("type: %s, id: %s\n" % (type, id) +
                           "El tipo es inválido")
            return False
    return True
