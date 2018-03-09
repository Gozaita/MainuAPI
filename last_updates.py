from flask import request, jsonify
from flask_httpauth import HTTPBasicAuth
from time import localtime, strftime
import logging
import json
import sys

ROOT = ''  # ${ROOT_PATH} for production mode

PATH = ROOT + 'last_updates/'
MAIN = PATH + 'main.json'
BOCD = PATH + 'bocadillos.json'
PLAT = PATH + 'platos.json'
OTHS = PATH + 'otros.json'

USRS = ROOT + 'users.json'

logger = logging.getLogger(__name__)

auth = HTTPBasicAuth()
users = json.load(open(USRS, 'r'))

main = {}
bocd = {}
plat = {}
oths = {}


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None


def setup():
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


def auth_setup(a):
    global auth
    auth = a

#############################################
# API Methods
#############################################


def get_last_update(type, id=None):
    """
    Devuelve la última fecha en la que se ha actualizado la lista de <type>,
    donde <type> puede ser:
    - bocadillos
    - menu
    - otros
    Si se pasa además el parámetro <id> se devolverá información del
    bocadillo, plato del menú u otro (p. ej.: /last_update/menu/5).
    """
    logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                "Devuelve última fecha de modificación")
    res = ''
    if id is None:
        if type == 'bocadillos' or type == 'menu' or type == 'otros':
            logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                        "type: %s" % type)
            logger.info("El tamaño de main es %d" % len(main))
            res = main[type]
        else:
            logger.warning("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                           "type: %s\n" % type +
                           "El tipo es inválido")
    else:
        if type == 'bocadillos':
            logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                        "type: %s, id: %s" % (type, id))
            res = bocd[id]
        elif type == 'menu':
            logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                        "type: %s, id: %s" % (type, id))
            res = plat[id]
        elif type == 'otros':
            logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                        "type: %s, id: %s" % (type, id))
            res = oths[id]
        else:
            logger.warning("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                           "type: %s, id: %s\n" % (type, id) +
                           "El tipo es inválido")
    return jsonify(res)


def modify_last_update(type, id=None):
    """
    Actualiza la última fecha de modificación en last_updates. No es necesario
    que se pase la fecha ni la hora, la función será la responsable de
    introducirla.
    """
    logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                "Actualiza la última fecha de modificación")

    time = strftime("%Y-%m-%d %H:%M:%S", localtime())
    if id is None:
        if type == 'bocadillos' or type == 'menu' or type == 'otros':
            logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                        "type: %s" % type)
            main[type] = time
            write(main)
        else:
            logger.warning("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                           "type: %s\n" % type +
                           "El tipo es inválido")
            return jsonify(False)
    else:
        if type == 'bocadillos':
            logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                        "type: %s, id: %s" % (type, id))
            bocd[id] = time
            write(bocd)
        elif type == 'menu':
            logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                        "type: %s, id: %s" % (type, id))
            plat[id] = time
            write(plat)
        elif type == 'otros':
            logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                        "type: %s, id: %s" % (type, id))
            oths[id] = time
            write(oths)
        else:
            logger.warning("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                           "type: %s, id: %s\n" % (type, id) +
                           "El tipo es inválido")
            return jsonify(False)
    return jsonify(True)
