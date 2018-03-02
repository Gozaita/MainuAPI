# -*- coding: utf-8 -*-
from flask import Flask, jsonify, redirect, request
from sqlalchemy import create_engine
from time import localtime, strftime
from logging.handlers import TimedRotatingFileHandler
import os
import logging
import sys
import json

URI = open('.mainudb', 'r').read()
LOG_PATH = 'log/mainu.log'

UPD_PATH = 'updates/'
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

    handler = TimedRotatingFileHandler(path,
                                       when="D",
                                       interval=1,
                                       backupCount=7)
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
# Bocadillos
#############################################


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
       2.1. Recoge todas las filas y columnas de la tabla IngredienteBocadillo
            donde el Bocadillo_id se corresponde con el id del elemento
            en cuestión.
       2.2. Para cada elemento de los recogidos en el 2.1, acude a la tabla
            Ingrediente para recuperar el nombre utilizando el Ingrediente_id.
       2.3. Todos los nombres de los ingredientes son añadidos a un array.
       2.4. Se insertan en un diccionario todos los elementos que se van a
            devolver para cada bocadillo, incluyendo la lista de ingredientes.
    3. Cada elemento, tras realizar las tareas del punto 2, se añaden a un
       array, que se devuelve en formato JSON.
    """
    app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                    "Devuelve lista completa de los bocadillos")
    try:
        cx = db.connect()
        bocs = cx.execute("SELECT * FROM Bocadillo")
        bocs_final = []
        for b in bocs:
            ings_id = cx.execute("SELECT * FROM IngredienteBocadillo " +
                                 "WHERE Bocadillo_id=%d" % b['id'])
            ings = []
            for i in ings_id:
                ing = cx.execute("SELECT Ingrediente.nombre FROM " +
                                 "Ingrediente WHERE Ingrediente.id=%d"
                                 % i['Ingrediente_id']).fetchone()
                ings.append(ing['nombre'])
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
    app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                    "Devuelve bocadillo: id %d" % id)
    try:
        cx = db.connect()
        b = cx.execute("SELECT * FROM Bocadillo WHERE Bocadillo.id=%d"
                       % id).fetchone()
        ings_id = cx.execute("SELECT * FROM IngredienteBocadillo " +
                             "WHERE Bocadillo_id=%d" % id)
        ings = []
        for i in ings_id:
            ing = cx.execute("SELECT Ingrediente.nombre FROM " +
                             "Ingrediente WHERE Ingrediente.id=%d"
                             % i['Ingrediente_id']).fetchone()
            ings.append(ing['nombre'])

        im = cx.execute("SELECT FotoBocadillo.ruta FROM FotoBocadillo " +
                        "WHERE FotoBocadillo.Bocadillo_id=%d " % id +
                        "AND FotoBocadillo.visible=True AND " +
                        "FotoBocadillo.oficial=True").fetchone()
        if im is not None:
            img = BOC_PATH + im['ruta']
        else:
            img = None

        vals_id = cx.execute("SELECT * FROM ValoracionBocadillo " +
                             "WHERE Bocadillo_id=%d" % id)
        vals = []
        for v in vals_id:
            val = cx.execute("SELECT v.id, v.texto, v.puntuacion, " +
                             "u.nombre, u.foto FROM ValoracionBocadillo " +
                             "AS v INNER JOIN Usuario AS u ON " +
                             "v.Usuario_id=u.id WHERE v.id=%d " % v['id'] +
                             "AND v.visible=True").fetchone()
            vals.append(dict(zip(val.keys(), val)))

        boc = {'id': b['id'], 'nombre': b['nombre'], 'precio': b['precio'],
               'puntuacion': b['puntuacion'], 'ingredientes': ings,
               'imagen': img, 'valoraciones': vals}
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
       2.1. Recoge de la tabla FotoPlato el campo ruta de la primera fila
            cuyo Plato_id coincida con el del elemento de la iteración, y tenga
            el valor True en los campos 'oficial' y 'visible'. Si se ha
            devuelto una imagen (im is not None), se establece la ruta
            completa para la imagen del plato añadiéndole el prefijo definido
            al inicio (PLT_PATH).
       2.2. Se insertan en un diccionario todos los elementos que se van a
            devolver para cada plato, incluyendo la ruta de la imagen.
       2.3. Se comprueba si el tipo del plato es 1 (primero), 2 (segundo)
            o 3 (postre). En función de ello, se añade a un array u otro.
    3. Se deuvelve en formato JSON el diccionario con los tres arrays.
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
            im = cx.execute("SELECT FotoPlato.ruta FROM FotoPlato WHERE " +
                            "FotoPlato.Plato_id=%d AND " % p['id'] +
                            "FotoPlato.oficial=True AND " +
                            "FotoPlato.visible=True").fetchone()
            if im is not None:
                img = PLT_PATH + im['ruta']
            else:
                img = None
            pl = {'id': p['id'], 'nombre': p['nombre'],
                  'puntuacion': p['puntuacion'], 'imagen': img}
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
    app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                    "Devuelve plato: id %d" % id)
    try:
        cx = db.connect()
        p = cx.execute("SELECT * FROM Plato WHERE Plato.id=%d"
                       % id).fetchone()

        im = cx.execute("SELECT FotoPlato.ruta FROM FotoPlato " +
                        "WHERE FotoPlato.Plato_id=%d " % id +
                        "AND FotoPlato.visible=True AND " +
                        "FotoPlato.oficial=True").fetchone()
        if im is not None:
            img = PLT_PATH + im['ruta']
        else:
            img = None

        vals_id = cx.execute("SELECT * FROM ValoracionPlato " +
                             "WHERE Plato_id=%d" % id)
        vals = []
        for v in vals_id:
            val = cx.execute("SELECT v.id, v.texto, v.puntuacion, " +
                             "u.nombre, u.foto FROM ValoracionPlato " +
                             "AS v INNER JOIN Usuario AS u ON " +
                             "v.Usuario_id=u.id WHERE v.id=%d " % v['id'] +
                             "AND v.visible=True").fetchone()
            vals.append(dict(zip(val.keys(), val)))

        plt = {'id': p['id'], 'nombre': p['nombre'], 'puntuacion':
               p['puntuacion'], 'descripcion': p['descripcion'],
               'tipo': p['tipo'], 'imagen': img, 'valoraciones': vals}
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
    app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                    "Devuelve otros elementos")
    try:
        cx = db.connect()
        otros = cx.execute("SELECT * FROM Otro")
        otros_final = []
        for o in otros:
            im = cx.execute("SELECT FotoOtro.ruta FROM " +
                            "FotoOtro WHERE " +
                            "FotoOtro.Otro_id=%d " % o['id'] +
                            "AND FotoOtro.oficial=True AND " +
                            "FotoOtro.visible=True").fetchone()
            if im is not None:
                img = OTH_PATH + im['ruta']
            else:
                img = None
            otro = {'id': o['id'], 'nombre': o['nombre'], 'precio':
                    o['precio'], 'puntuacion': o['puntuacion'], 'imagen': img}
            otros_final.append(otro)
        return jsonify(otros_final)
    except Exception:
        app.logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                             "Ha ocurrido una excepción durante la petición")
        return None


@app.route("/otros/<int:id>", methods=["GET"])
def get_otro_by_id(id):
    app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                    "Devuelve otro: id %d" % id)
    try:
        cx = db.connect()
        o = cx.execute("SELECT * FROM Otro WHERE Otro.id=%d"
                       % id).fetchone()

        im = cx.execute("SELECT FotoOtro.ruta FROM FotoOtro " +
                        "WHERE FotoOtro.Otro_id=%d " % id +
                        "AND FotoOtro.visible=True AND " +
                        "FotoOtro.oficial=True").fetchone()
        if im is not None:
            img = OTH_PATH + im['ruta']
        else:
            img = None

        vals_id = cx.execute("SELECT * FROM ValoracionOtro " +
                             "WHERE Otro_id=%d" % id)
        vals = []
        for v in vals_id:
            val = cx.execute("SELECT v.id, v.texto, v.puntuacion, " +
                             "u.nombre, u.foto FROM ValoracionOtro " +
                             "AS v INNER JOIN Usuario AS u ON " +
                             "v.Usuario_id=u.id WHERE v.id=%d " % v['id'] +
                             "AND v.visible=True").fetchone()
            vals.append(dict(zip(val.keys(), val)))

        otr = {'id': o['id'], 'nombre': o['nombre'], 'puntuacion':
               o['puntuacion'], 'imagen': img, 'valoraciones': vals}
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
    """
    app.logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                    "Devuelve última fecha de modificación")
    if id is None:
        if type == 'bocadillo' or 'menu' or 'otros':
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
