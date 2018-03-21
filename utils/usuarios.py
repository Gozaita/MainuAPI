# -*- coding: utf-8 -*-
from google.oauth2 import id_token
from google.auth.transport import requests
import logging

ROOT = ''  # ${ROOT_PATH} for production mode

CLIENT_ID = ''

logger = logging.getLogger(__name__)


def setup(r):
    global ROOT, CLIENT_ID
    ROOT = r
    try:
        CLIENT_ID = open(ROOT + 'sens_data/.client_id', 'r').read()
        logger.info("Se ha accedido al CLIENT_ID")
    except Exception:
        logger.warning("Ha habido un problema al acceder al CLIENT_ID")


def verify_token(idToken):
    """
    Verifica la integridad del idToken entrante:
    1. La función verify_oauth2_token comprueba:
       - Que está firmado por Google.
       - Que el valor del campo <aud> se correponde con el CLIENT_ID de MainU.
       - Que el token no ha caducado.
    2. Se comprueba, además:
       - Que el valor del campo <iss> es accounts.google.com (o con HTTPS).
    En caso de fallar, se levanta un ValueError y devuelve un userid 'None'.
    """
    try:
        logger.info("Verifica la integridad del token recibido")
        idinfo = id_token.verify_oauth2_token(idToken, requests.Request(),
                                              CLIENT_ID)
        if idinfo['iss'] not in ['accounts.google.com',
                                 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        userid = idinfo['sub']
        name = idinfo['name']
        mail = idinfo['email']
        pic = idinfo['picture']

        logger.info("Token validado")
        return {'id': userid, 'nombre': name, 'mail': mail, 'foto': pic}
    except ValueError:
        logger.exception("La validación del token ha resultado negativa")
        return None


def add_user(id, nombre, mail, foto, cx):
    """
    Añade un usuario nuevo a la base de datos. Se le debe pasar el <id> de
    usuario además del resto de datos.
    """
    logger.info("Añade usuario a la base de datos")
    try:
        cx.execute("INSERT INTO Usuario (id, nombre, mail, foto) VALUES " +
                   "(\"%s\", \"%s\", \"%s\", \"%s\")" % (id, nombre,
                                                         mail, foto))
        return True
    except Exception:
        logger.exception("Ha ocurrido un error al añadir el usuario")
        return None


def user_exists(id, cx):
    """
    Comprueba si un usuario existe o no en la base de datos utilizando su <id>.
    Si el usuario existe, devuelve un objeto de tipo Usuario, con la
    información del mismo. Si el usuario no existe, devuelve None.
    """
    logger.info("Comprueba la existencia del usuario: %s" % id)
    try:
        u = cx.execute("SELECT * FROM Usuario WHERE id=\"%s\"" % id).fetchone()

        if u is not None:
            user = {'id': u['id'], 'nombre': u['nombre'], 'foto': u['foto'],
                    'verificado': u['verificado']}
            return user
        else:
            return None
    except Exception:
        logger.exception("Ha ocurrido un error al comprobar el usuario")
        return None
