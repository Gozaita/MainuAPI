from time import localtime, strftime
import logging
import json
import sys

ROOT = ''  # ${ROOT_PATH} for production mode

PATH = ''
MAIN = ''
BOCD = ''
PLAT = ''
OTHS = ''

logger = logging.getLogger(__name__)

main = {}
bocd = {}
plat = {}
oths = {}


def setup(r):
    global ROOT, PATH, MAIN, BOCD, PLAT, OTHS
    ROOT = r
    PATH = ROOT + 'last_updates/'
    MAIN = PATH + 'main.json'
    BOCD = PATH + 'bocadillos.json'
    PLAT = PATH + 'platos.json'
    OTHS = PATH + 'otros.json'

    global main, bocd, plat, oths

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
    res = ''
    if id is None:
        if type == 'bocadillos' or type == 'menu' or type == 'otros':
            logger.info("type: %s" % type)
            logger.info("El tamaño de main es %d" % len(main))
            res = main[type]
        else:
            logger.warning("type: %s\n" % type +
                           "El tipo es inválido")
    else:
        if type == 'bocadillos':
            logger.info("type: %s, id: %s" % (type, id))
            res = bocd[id]
        elif type == 'menu':
            logger.info("type: %s, id: %s" % (type, id))
            res = plat[id]
        elif type == 'otros':
            logger.info("type: %s, id: %s" % (type, id))
            res = oths[id]
        else:
            logger.warning("type: %s, id: %s\n" % (type, id) +
                           "El tipo es inválido")
    return res


def modify_last_update(type, id=None):
    time = strftime("%Y-%m-%d %H:%M:%S", localtime())
    if id is None:
        if type == 'bocadillos' or type == 'menu' or type == 'otros':
            logger.info("type: %s" % type)
            main[type] = time
            write(main)
        else:
            logger.warning("type: %s\n" % type +
                           "El tipo es inválido")
            return False
    else:
        if type == 'bocadillos':
            logger.info("type: %s, id: %s" % (type, id))
            bocd[id] = time
            write(bocd)
        elif type == 'menu':
            logger.info("type: %s, id: %s" % (type, id))
            plat[id] = time
            write(plat)
        elif type == 'otros':
            logger.info("type: %s, id: %s" % (type, id))
            oths[id] = time
            write(oths)
        else:
            logger.warning("type: %s, id: %s\n" % (type, id) +
                           "El tipo es inválido")
            return False
    return True
