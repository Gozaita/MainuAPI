# -*- coding: utf-8 -*-
from flask import Flask, jsonify, redirect, request
from sqlalchemy import create_engine
from time import localtime, strftime
from logging.handlers import TimedRotatingFileHandler
from google.oauth2 import id_token
from google.auth.transport import requests
import os
import logging
import sys
import json

ROOT = ''  # ${ROOT_PATH} for production mode

URI = open(ROOT + '.mainudb', 'r').read()
CLIENT_ID = open(ROOT + '.client_id', 'r').read()
LOG_PATH = ROOT + 'log/mainu.log'

UPD_PATH = ROOT + 'last_updates/'
UPD_MAIN = UPD_PATH + 'main.json'
UPD_BOCD = UPD_PATH + 'bocadillos.json'
UPD_PLAT = UPD_PATH + 'platos.json'
UPD_OTHS = UPD_PATH + 'otros.json'

SRV_PATH = 'https://server.mainu.eus/'
IMG_PATH = SRV_PATH + 'external/images/'
BOC_PATH = IMG_PATH + 'bocadillos/'
PLT_PATH = IMG_PATH + 'platos/'
OTH_PATH = IMG_PATH + 'otros/'

API_MAIN = "https://www.mainu.eus/api"

#############################################
# MainU Log
#############################################


def log_setup(path):
    try:
        log = open(path, 'a')
    except FileNotFoundError:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        log = open(path, 'w')

    log.write("##############################################\n")
    log.write("MainU -- mainu.eus -- %s\n"
              % strftime("%Y-%m-%d %H:%M:%S", localtime()))
    log.write("API REST\n")
    log.write("##############################################\n")
    log.close()

    handler = TimedRotatingFileHandler(filename=path,
                                       when='midnight',
                                       backupCount=10,
                                       encoding="utf-8")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s]: %(levelname)s - ' +
                                  '%(funcName)s - %(message)s')
    handler.setFormatter(formatter)
    return handler

#############################################
# Last updates
#############################################


def updates_setup(mainp, bocdp, platp, othsp):
    try:
        mainf = open(mainp, 'r')
        app.logger.info("Se ha encontrado el fichero: %s"
                        % mainp)
        bocdf = open(bocdp, 'r')
        app.logger.info("Se ha encontrado el fichero: %s"
                        % bocdp)
        platf = open(platp, 'r')
        app.logger.info("Se ha encontrado el fichero: %s"
                        % platp)
        othsf = open(othsp, 'r')
        app.logger.info("Se ha encontrado el fichero: %s"
                        % othsp)
    except FileNotFoundError:
        app.logger.error("No se ha podido acceder a uno o varios de los " +
                         "directorios de actualización")
        sys.exit(1)

    upd_main = json.load(mainf)
    mainf.close()
    upd_bocd = json.load(bocdf)
    bocdf.close()
    upd_plat = json.load(platf)
    platf.close()
    upd_oths = json.load(othsf)
    othsf.close()

    app.logger.info("El tamaño de upd_main es %d" % len(upd_main))
    app.logger.info("El tamaño de upd_bocd es %d" % len(upd_bocd))
    app.logger.info("El tamaño de upd_plat es %d" % len(upd_plat))
    app.logger.info("El tamaño de upd_oths es %d" % len(upd_oths))

    return upd_main, upd_bocd, upd_plat, upd_oths


def updates_write(dict):
    if dict is upd_main:
        path = UPD_MAIN
    if dict is upd_bocd:
        path = UPD_BOCD
    if dict is upd_plat:
        path = UPD_PLAT
    if dict is upd_oths:
        path = UPD_OTHS
    try:
        file = open(path, 'w')
        json.dump(dict, file)
        file.close()
        return True
    except FileNotFoundError:
        app.logger.warning("No se puede acceder al directorio de " +
                           "actualización %s. No se realizará el " % path +
                           "volcado de datos")
        return False

#############################################
# Inicialización
#############################################


db = create_engine(URI)
app = Flask(__name__)

handler = log_setup(LOG_PATH)
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

upd_main, upd_bocd, upd_plat, upd_oths = updates_setup(UPD_MAIN, UPD_BOCD,
                                                       UPD_PLAT, UPD_OTHS)

#############################################
# MainU API
#############################################

#############################################
# Usuarios
#############################################


# TODO: add_user(id, nombre, mail, foto)


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
        app.logger.info("Verifica la integridad del token recibido")
        idinfo = id_token.verify_oauth2_token(idToken, requests.Request(),
                                              CLIENT_ID)
        if idinfo['iss'] not in ['accounts.google.com',
                                 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        userid = idinfo['sub']
        name = idinfo['name']
        mail = idinfo['email']
        pic = idinfo['picture']

        app.logger.info("Token validado")
        return userid, name, mail, pic
    except ValueError:
        app.logger.exception("La validación del token ha resultado negativa")
        return None

#############################################
# Imágenes
#############################################


# TODO: add_image(idToken, type, id, image)


def get_imgs(type, id, cx=None):
    """
    Devuelve todas las imágenes asociadas a un elemento con un <id> del
    tipo <type> que se especifique. Si no existe una conexión creada con
    la base de datos (no se le pasa el parámetro <cx>), intentará crear
    una nueva. La primera imagen de la lista es la marcada como 'oficial'.
    Cada imagen contiene:
    - id
    - url
    - usuario:
        - id
        - nombre
        - foto
        - verificado
    Tareas que realiza:
    1. En función del parámetro <type>, inicializa las variables que se
       utilizarán. Si el parámetro no se corresponde con ninguno de los
       esperados, levantará una excepción.
    2. Si no se ha pasado el parámetro <cx>, se inicia una conexión.
    3. Realiza una búsqueda de las imágenes asociadas al <id> del elemento,
       recuperando también los datos del usuario correspondiente a cada imagen.
    4. Se estructuran los datos recuperados y se devuelve un array de imágenes.
    """
    try:
        if type == 'bocadillos':
            ft = 'FotoBocadillo'
            cl = 'Bocadillo_id'
            path = BOC_PATH
        elif type == 'menu':
            ft = 'FotoPlato'
            cl = 'Plato_id'
            path = PLT_PATH
        elif type == 'otros':
            ft = 'FotoOtro'
            cl = 'Otro_id'
            path = OTH_PATH
        else:
            raise Exception

        if cx is None:
            cx = db.connect()

        ims = cx.execute("SELECT i.id, i.ruta, i.Usuario_id, " +
                         "u.nombre, u.foto, u.verificado FROM %s AS i " % ft +
                         "INNER JOIN Usuario AS u ON u.id=Usuario_id " +
                         "WHERE visible=True AND %s=%d " % (cl, id) +
                         "ORDER BY oficial DESC")
        imgs = []
        if ims is not None:
            for i in ims:
                img = path + i['ruta']
                us = {'id': i['Usuario_id'], 'nombre': i['nombre'],
                      'foto': i['foto'], 'verificado': i['verificado']}
                imgs.append({'id': i['id'], 'url': img, 'usuario': us})

        return imgs
    except Exception:
        app.logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                             "Ha ocurrido una excepción durante la petición")
        return None

#############################################
# Valoraciones
#############################################


# TODO: add_valoration(idToken, type, id, valoration)


def get_vals(type, id, cx=None):
    """
    Devuelve todas las valoraciones asociadas a un elemento con un <id> del
    tipo <type> que se especifique. Si no existe una conexión creada con
    la base de datos (no se le pasa el parámetro <cx>), intentará crear
    una nueva. Cada valoración contiene:
    - id
    - puntuación
    - texto
    - usuario:
        - id
        - nombre
        - foto
        - verificado
    Tareas que realiza:
    1. En función del parámetro <type>, inicializa las variables que se
       utilizarán. Si el parámetro no se corresponde con ninguno de los
       esperados, levantará una excepción.
    2. Si no se ha pasado el parámetro <cx>, se inicia una conexión.
    3. Realiza una búsqueda de las valoraciones asociadas al <id> del elemento,
       recuperando también los datos del usuario correspondiente a cada
       valoración.
    4. Se estructuran los datos recuperados y se devuelve un array de
       valoraciones.
    """
    try:
        if type == 'bocadillos':
            vt = 'ValoracionBocadillo'
            cl = 'Bocadillo_id'
        elif type == 'menu':
            vt = 'ValoracionPlato'
            cl = 'Plato_id'
        elif type == 'otros':
            vt = 'ValoracionOtro'
            cl = 'Otro_id'
        else:
            raise Exception

        if cx is None:
            cx = db.connect()

        vls = cx.execute("SELECT v.id, v.puntuacion, v.texto, v.Usuario_id, " +
                         "u.nombre, u.foto, u.verificado FROM %s AS v " % vt +
                         "INNER JOIN Usuario AS u ON u.id=Usuario_id " +
                         "WHERE visible=True AND %s=%d" % (cl, id))
        vals = []
        if vls is not None:
            for v in vls:
                us = {'id': v['Usuario_id'], 'nombre': v['nombre'],
                      'foto': v['foto'], 'verificado': v['verificado']}
                val = {'id': v['id'], 'puntuacion': v['puntuacion'],
                       'texto': v['texto'], 'usuario': us}
                vals.append(val)

        return vals
    except Exception:
        app.logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                             "Ha ocurrido una excepción durante la petición")
        return None

#############################################
# Bocadillos
#############################################


def get_ings(id, cx=None):
    """
    Devuelve todos los ingredientes asociados al bocadillo con el <id>
    especificado. Si no existe una conexión creada con la base de datos
    (no se le pasa el parámetro <cx>), intentará crear una nueva. cada
    ingrediente contiene:
    - id
    - nombre
    Tareas que realiza:
    1. Si no se ha pasado el parámetro <cx>, se inicia una conexión.
    2. Realiza una búsqueda de los ingredientes asociados al <id> del
       bocadillo, recuperando datos de las tablas IngredienteBocadillo
       (relaciones entre ingredientes y bocadillos) e Ingrediente
       (relación entre id y nombre de ingrediente).
    4. Se estructuran los datos recuperados y se devuelve un array de
       valoraciones.
    """
    try:
        if cx is None:
            cx = db.connect()

        ins = cx.execute("SELECT ib.Ingrediente_id, i.nombre FROM " +
                         "IngredienteBocadillo AS ib INNER JOIN Ingrediente " +
                         "AS i ON Ingrediente_id=i.id "
                         "WHERE Bocadillo_id=%d" % id)
        ings = []
        for i in ins:
            ing = {'id': i['Ingrediente_id'], 'nombre': i['nombre']}
            ings.append(ing)

        return ings
    except Exception:
        app.logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                             "Ha ocurrido una excepción durante la petición")
        return None


@app.route("/bocadillos", methods=["GET"])
def get_bocadillos():
    """
    Devuelve una lista de bocadillos. Para cada uno:
    - id
    - nombre
    - precio
    - puntuacion
    - ingredientes
    Tareas que realiza:
    1. Recoge todas las filas y columnas de la tabla Bocadillo.
    2. Para cada elemento de los recogidos:
       2.1. Llama a get_ings para recoger los ingredientes correspondientes
            a este bocadillo.
       2.2. Introduce en un diccionario todos los elementos a devolver,
            incluyendo la lista de ingredientes.
    3. Se devuelve una lista en formato JSON.
    """
    app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                    "Devuelve lista completa de los bocadillos")
    try:
        cx = db.connect()
        bocs = cx.execute("SELECT * FROM Bocadillo")
        bocs_final = []
        for b in bocs:
            ings = get_ings(b['id'], cx)
            boc = {'id': b['id'], 'nombre': b['nombre'], 'precio': b['precio'],
                   'puntuacion': b['puntuacion'], 'ingredientes': ings}
            bocs_final.append(boc)
        return jsonify(bocs_final)
    except Exception:
        app.logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                             "Ha ocurrido una excepción durante la petición")
        return None


@app.route("/bocadillos/<int:id>", methods=["GET"])
def get_bocadillo_by_id(id):
    """
    Devuelve la información asociada a un bocadillo con el <id> especificado:
    - id
    - nombre
    - precio
    - puntuacion
    - ingredientes (via get_ings)
    - images (via get_imgs)
    - valoraciones (via get_vals)
    Tareas que realiza:
    1. Recupera de la base de datos la información de la tabla Bocadillo
       correspondiente al elemento con el <id> especificado.
    2. Realiza llamadas a las funciones get_ings, get_imgs y get_vals para
       recuperar los ingredientes, imágenes y valoraciones.
    3. Se estructuran los datos recuperados y se devuelve la información
       en formato JSON.
    """
    app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                    "Devuelve bocadillo: id %d" % id)
    try:
        cx = db.connect()
        b = cx.execute("SELECT * FROM Bocadillo WHERE Bocadillo.id=%d"
                       % id).fetchone()
        ings = get_ings(id, cx)
        imgs = get_imgs('bocadillos', id, cx)
        vals = get_vals('bocadillos', id, cx)

        boc = {'id': b['id'], 'nombre': b['nombre'], 'precio': b['precio'],
               'puntuacion': b['puntuacion'], 'ingredientes': ings,
               'images': imgs, 'valoraciones': vals}
        return jsonify(boc)
    except Exception:
        app.logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                             "Ha ocurrido una excepción durante la petición")
        return None

#############################################
# Platos
#############################################


@app.route("/menu", methods=["GET"])
def get_menu():
    """
    Devuelve el menú del día usando un diccionario de tres arrays:
    - primeros
    - segundos
    - postre
    Cada elemento de cualquiera de los arrays contiene:
    - id
    - nombre
    - puntuacion
    - imagen
    Tareas que realiza:
    1. Recoge todos los elementos de la tabla Plato que tengan el valor True
       en la columna 'actual'. Esto hace que únicamente recoja los elementos
       que se encuentran en el menú del día.
    2. Para cada elemento de los recogidos:
       2.1. Llama a get_imgs para recuperar las imágenes asociadas al plato.
            Si la lista recuperada no está vacía, se obtiene su primer elemento
            (imagen oficial) y se descarta el resto. NOTA: Aunque solamente se
            envíe un elemento, éste se encuentra dentro de un array para ser
            coherente con la estructura del objeto Plato ('images' es array).
       2.2. Se insertan en un diccionario todos los elementos que se van a
            devolver para cada plato.
       2.3. Se comprueba si el tipo del plato es 1 (primero), 2 (segundo)
            o 3 (postre). En función de ello, se añade a un array u otro.
    3. Se devuelve en formato JSON el diccionario con los tres arrays.
    """
    app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                    "Devuelve menú del día")
    try:
        cx = db.connect()
        menu = cx.execute("SELECT * FROM Plato WHERE actual=True")
        pr = []
        sg = []
        ps = []
        for p in menu:
            imgs = get_imgs('menu', p['id'], cx)
            if imgs:
                imgs = [imgs[0]]

            pl = {'id': p['id'], 'nombre': p['nombre'],
                  'puntuacion': p['puntuacion'], 'images': imgs}
            if p['tipo'] == 1:
                pr.append(pl)
            elif p['tipo'] == 2:
                sg.append(pl)
            else:
                ps.append(pl)
        return jsonify({'primeros': pr, 'segundos': sg, 'postre': ps})
    except Exception:
        app.logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                             "Ha ocurrido una excepción durante la petición")
        return None


@app.route("/menu/<int:id>", methods=["GET"])
def get_plato_by_id(id):
    """
    Devuelve la información asociada a un plato con el <id> especificado:
    - id
    - nombre
    - puntuacion
    - descripcion
    - tipo
    - images (via get_imgs)
    - valoraciones (via get_vals)
    Tareas que realiza:
    1. Recupera de la base de datos la información de la tabla Plato
       correspondiente al elemento con el <id> especificado.
    2. Realiza llamadas a las funciones get_imgs y get_vals para recuperar las
       imágenes y valoraciones.
    3. Se estructuran los datos recuperados y se devuelve la información
       en formato JSON.
    """
    app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                    "Devuelve plato: id %d" % id)
    try:
        cx = db.connect()
        p = cx.execute("SELECT * FROM Plato WHERE Plato.id=%d"
                       % id).fetchone()

        imgs = get_imgs('menu', id, cx)
        vals = get_vals('menu', id, cx)

        plt = {'id': p['id'], 'nombre': p['nombre'], 'puntuacion':
               p['puntuacion'], 'descripcion': p['descripcion'],
               'tipo': p['tipo'], 'images': imgs, 'valoraciones': vals}
        return jsonify(plt)
    except Exception:
        app.logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                             "Ha ocurrido una excepción durante la petición")
        return None

#############################################
# Otros
#############################################


@app.route("/otros", methods=["GET"])
def get_otros():
    """
    Devuelve una lista de otros productos. Para cada uno:
    - id
    - nombre
    - precio
    - puntuacion
    - imagen
    Tareas que realiza:
    1. Recoge todas las filas y columnas de la tabla Otro.
    2. Para cada elemento de los recogidos:
       2.1. Llama a get_imgs para recuperar las imágenes asociadas al producto.
            Si la lista recuperada no está vacía, se obtiene su primer elemento
            (imagen oficial) y se descarta el resto. NOTA: Aunque solamente se
            envíe un elemento, éste se encuentra dentro de un array para ser
            coherente con la estructura del objeto Otro ('images' es array).
       2.2. Se insertan en un diccionario todos los elementos que se van a
            devolver para cada producto, incluyendo la ruta de la imagen.
    3. Cada elemento, tras realizar las tareas del punto 2, se añade a un
       array, que se devuelve en formato JSON.
    """
    app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                    "Devuelve otros elementos")
    try:
        cx = db.connect()
        otros = cx.execute("SELECT * FROM Otro")
        otros_final = []
        for o in otros:
            imgs = get_imgs('otros', o['id'], cx)
            if imgs is not None:
                imgs = [imgs[0]]

            otro = {'id': o['id'], 'nombre': o['nombre'], 'precio':
                    o['precio'], 'puntuacion': o['puntuacion'], 'images': imgs}
            otros_final.append(otro)
        return jsonify(otros_final)
    except Exception:
        app.logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                             "Ha ocurrido una excepción durante la petición")
        return None


@app.route("/otros/<int:id>", methods=["GET"])
def get_otro_by_id(id):
    """
    Devuelve la información asociada a un producto de la categoría 'otros'
    con el <id> especificado:
    - id
    - nombre
    - puntuacion
    - precio
    - images (via get_imgs)
    - valoraciones (via get_vals)
    Tareas que realiza:
    1. Recupera de la base de datos la información de la tabla Otro
       correspondiente al elemento con el <id> especificado.
    2. Realiza llamadas a las funciones get_imgs y get_vals para recuperar las
       imágenes y valoraciones.
    3. Se estructuran los datos recuperados y se devuelve la información
       en formato JSON.
    """
    app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                    "Devuelve otro: id %d" % id)
    try:
        cx = db.connect()
        o = cx.execute("SELECT * FROM Otro WHERE Otro.id=%d"
                       % id).fetchone()

        imgs = get_imgs('otros', id, cx)
        vals = get_vals('otros', id, cx)

        otr = {'id': o['id'], 'nombre': o['nombre'], 'puntuacion':
               o['puntuacion'], 'precio': o['precio'], 'images': imgs,
               'valoraciones': vals}
        return jsonify(otr)
    except Exception:
        app.logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                             "Ha ocurrido una excepción durante la petición")
        return None

#############################################
# Generales
#############################################


@app.route("/last_update/<type>", methods=["GET"])
@app.route("/last_update/<type>/<id>", methods=["GET"])
def last_update(type, id=None):
    """
    Devuelve la última fecha en la que se ha actualizado la lista de <type>,
    donde <type> puede ser:
    - bocadillos
    - menu
    - otros
    Si se pasa además el parámetro <id> se devolverá información del
    bocadillo, plato del menú u otro (p. ej.: /last_update/menu/5).
    Tareas que realiza:
    1. Comprueba si se ha pasado un <id> o no.
    2. Si no se ha pasado un <id>, se buscará en el diccionario upd_main el
       elemento <type> (en caso de que se haya pasado un tipo válido) y se
       devolverá su valor.
    3. Si se ha pasado un <id>, se acudirá a upd_bocd, upd_plat o upd_oths
       dependiendo del tipo y se buscará el elemento <id> en uno de esos
       diccionarios, devolviendo el valor obtenido.
    4. En cualquier caso, si el tipo no es válido, se devolverá una cadena
       vacía.
    """
    app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                    "Devuelve última fecha de modificación")
    res = ''
    if id is None:
        if type == 'bocadillo' or type == 'menu' or type == 'otros':
            app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                            "type: %s" % type)
            res = upd_main[type]
        else:
            app.logger.warning("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                               "type: %s\n" % type +
                               "El tipo es inválido")
    else:
        if type == 'bocadillos':
            app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                            "type: %s, id: %s" % (type, id))
            res = upd_bocd[id]
        elif type == 'menu':
            app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                            "type: %s, id: %s" % (type, id))
            res = upd_plat[id]
        elif type == 'otros':
            app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                            "type: %s, id: %s" % (type, id))
            res = upd_oths[id]
        else:
            app.logger.warning("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                               "type: %s, id: %s\n" % (type, id) +
                               "El tipo es inválido")
    return jsonify(res)


@app.route("/", methods=["GET"])
def api_main():
    """
    Redirige a la página de información sobre la API
    """
    app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                    "Redirige a %s" % API_MAIN)
    return redirect(API_MAIN)


if __name__ == '__main__':
    app.run()
