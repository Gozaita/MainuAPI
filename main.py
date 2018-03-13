# -*- coding: utf-8 -*-
from flask import Flask, jsonify, redirect, request
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import create_engine
from utils import updates, usuarios, bocadillos, imagenes, valoraciones
from utils import logger as log
import logging
import json

ROOT = ''   # ${ROOT_PATH} for production mode
IMG_ROOT = ''  # ${ROOT_PATH} for production mode

URI = open(ROOT + 'sens_data/.mainudb', 'r').read()

API_MAIN = "https://www.mainu.eus/api"

db = create_engine(URI)
app = Flask(__name__)

log.setup(ROOT)
updates.setup(ROOT)
usuarios.setup(ROOT)
imagenes.setup(IMG_ROOT)
valoraciones.setup(ROOT)

handler = log.get_handler()
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

auth = HTTPBasicAuth()
users = json.load(open(ROOT + 'sens_data/.users.json', 'r'))


@auth.get_password
def get_pw(username):
    if username in users:
        return users.get(username)
    return None

#############################################
# MainU API
#############################################

#############################################
# Imágenes
#############################################


# TODO: add_image(idToken, type, id, image)

#############################################
# Valoraciones
#############################################


# TODO: add_valoration(idToken, type, id, valoration)


@app.route("/valoraciones/<type>", methods=["GET"])
@auth.login_required
def get_invisible_vals(type):
    """
    Devuelve todas las valoraciones ocultas para elementos del <type>
    especificado.
    """
    try:
        cx = db.connect()
        r = valoraciones.get_invisible_vals(type, cx)
        cx.close
        return jsonify(r)
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return None


@app.route("/update_val/<type>/<int:id>", methods=["GET"])
@auth.login_required
def update_val(type, id):
    """
    Cambia el estado de una valoración con <id> especificado del <type>
    que se indique. Se le debe pasar como argumento la acción (action), que
    podrá tomar los valores 'visible' o 'delete'.
    """
    try:
        action = request.args.get('action', default=None)
        if action is None:
            raise Exception
        elif action != 'visible' and action != 'delete':
            raise Exception
        cx = db.connect()
        r = valoraciones.update_val(type, id, action, cx)
        cx.close
        return jsonify(r)
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return None

#############################################
# Bocadillos
#############################################


@app.route("/ingredientes", methods=["GET"])
def get_ingredientes():
    """
    Devuelve una lista de todos los ingredientes.
    """
    logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                "Devuelve lista completa de los ingredientes")
    try:
        cx = db.connect()
        ings = bocadillos.get_ings_all(cx)
        return jsonify(ings)
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return None


@app.route("/bocadillos", methods=["GET"])
def get_bocadillos():
    """
    Devuelve una lista de bocadillos.
    """
    logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                "Devuelve lista completa de los bocadillos")
    try:
        cx = db.connect()
        bocs = cx.execute("SELECT * FROM Bocadillo")
        bocs_final = []
        for b in bocs:
            ings = bocadillos.get_ings_by_id(b['id'], cx)
            boc = {'id': b['id'], 'nombre': b['nombre'], 'precio': b['precio'],
                   'puntuacion': b['puntuacion'], 'ingredientes': ings}
            bocs_final.append(boc)
        cx.close()
        return jsonify(bocs_final)
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return None


@app.route("/bocadillos/<int:id>", methods=["GET"])
def get_bocadillo_by_id(id):
    """
    Devuelve la información asociada a un bocadillo con el <id> especificado.
    """
    logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                "Devuelve bocadillo: id %d" % id)
    try:
        cx = db.connect()
        b = cx.execute("SELECT * FROM Bocadillo WHERE Bocadillo.id=%d"
                       % id).fetchone()
        ings = bocadillos.get_ings_by_id(id, cx)
        imgs = imagenes.get_imgs('bocadillos', id, cx)
        vals = valoraciones.get_vals('bocadillos', id, cx)
        cx.close()
        boc = {'id': b['id'], 'nombre': b['nombre'], 'precio': b['precio'],
               'puntuacion': b['puntuacion'], 'ingredientes': ings,
               'images': imgs, 'valoraciones': vals}
        return jsonify(boc)
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return None

#############################################
# Platos
#############################################


@app.route("/menu", methods=["GET"])
def get_menu():
    """
    Devuelve el menú del día usando un diccionario de tres arrays.
    """
    logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                "Devuelve menú del día")
    try:
        cx = db.connect()
        menu = cx.execute("SELECT * FROM Plato WHERE actual=True")
        pr = []
        sg = []
        ps = []
        for p in menu:
            imgs = imagenes.get_imgs('menu', p['id'], cx)
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
        cx.close()
        return jsonify({'primeros': pr, 'segundos': sg, 'postre': ps})
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return None


@app.route("/menu/<int:id>", methods=["GET"])
def get_plato_by_id(id):
    """
    Devuelve la información asociada a un plato con el <id> especificado.
    """
    logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                "Devuelve plato: id %d" % id)
    try:
        cx = db.connect()
        p = cx.execute("SELECT * FROM Plato WHERE Plato.id=%d"
                       % id).fetchone()

        imgs = imagenes.get_imgs('menu', id, cx)
        vals = valoraciones.get_vals('menu', id, cx)
        cx.close()
        plt = {'id': p['id'], 'nombre': p['nombre'], 'puntuacion':
               p['puntuacion'], 'descripcion': p['descripcion'],
               'tipo': p['tipo'], 'images': imgs, 'valoraciones': vals}
        return jsonify(plt)
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return None

#############################################
# Otros
#############################################


@app.route("/otros", methods=["GET"])
def get_otros():
    """
    Devuelve una lista de otros productos.
    """
    logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                "Devuelve otros elementos")
    try:
        cx = db.connect()
        otros = cx.execute("SELECT * FROM Otro")
        otros_final = []
        for o in otros:
            imgs = imagenes.get_imgs('otros', o['id'], cx)
            if imgs:
                imgs = [imgs[0]]

            otro = {'id': o['id'], 'nombre': o['nombre'], 'precio':
                    o['precio'], 'puntuacion': o['puntuacion'], 'images': imgs}
            otros_final.append(otro)
        cx.close()
        return jsonify(otros_final)
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return None


@app.route("/otros/<int:id>", methods=["GET"])
def get_otro_by_id(id):
    """
    Devuelve la información asociada a un producto de la categoría 'otros'
    con el <id> especificado.
    """
    logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                "Devuelve otro: id %d" % id)
    try:
        cx = db.connect()
        o = cx.execute("SELECT * FROM Otro WHERE Otro.id=%d"
                       % id).fetchone()

        imgs = imagenes.get_imgs('otros', id, cx)
        vals = valoraciones.get_vals('otros', id, cx)
        cx.close()
        otr = {'id': o['id'], 'nombre': o['nombre'], 'puntuacion':
               o['puntuacion'], 'precio': o['precio'], 'images': imgs,
               'valoraciones': vals}
        return jsonify(otr)
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return None

#############################################
# Last updates
#############################################


@app.route("/last_update/<type>", methods=["GET"])
@app.route("/last_update/<type>/<id>", methods=["GET"])
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
    if id is None:
        r = updates.get_last_update(type)
    else:
        r = updates.get_last_update(type, id)
    return jsonify(r)


@app.route("/update/<type>", methods=["GET"])
@app.route("/update/<type>/<id>", methods=["GET"])
@auth.login_required
def modify_last_update(type, id=None):
    """
    Actualiza la última fecha de modificación en last_updates. No es necesario
    que se pase la fecha ni la hora, la función será la responsable de
    introducirla.
    """
    logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                "Actualiza la última fecha de modificación")
    if id is None:
        r = updates.modify_last_update(type)
    else:
        r = updates.modify_last_update(type, id)
    return jsonify(r)

#############################################
# Generales
#############################################


@app.route("/", methods=["GET"])
def api_main():
    """
    Redirige a la página de información sobre la API.
    """
    logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                "Redirige a %s" % API_MAIN)
    return redirect(API_MAIN)


if __name__ == '__main__':
    app.run()
