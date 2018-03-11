# -*- coding: utf-8 -*-
from flask import Flask, jsonify, redirect, request
from sqlalchemy import create_engine
import utils.logger as log
import utils.updates as upd
import utils.users as usr
import utils.tools as tools
import logging

ROOT = ''  # ${ROOT_PATH} for production mode

URI = open(ROOT + 'sens_data/.mainudb', 'r').read()

API_MAIN = "https://www.mainu.eus/api"

db = create_engine(URI)
app = Flask(__name__)

log.ROOT = ROOT
log.setup()

upd.ROOT = ROOT
upd.setup()

usr.ROOT = ROOT
usr.setup()

handler = log.get_handler()
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)


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

#############################################
# Bocadillos
#############################################


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
            ings = tools.get_ings(b['id'], cx)
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
        ings = tools.get_ings(id, cx)
        imgs = tools.get_imgs('bocadillos', id, cx)
        vals = tools.get_vals('bocadillos', id, cx)
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
            imgs = tools.get_imgs('menu', p['id'], cx)
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

        imgs = tools.get_imgs('menu', id, cx)
        vals = tools.get_vals('menu', id, cx)
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
            imgs = tools.get_imgs('otros', o['id'], cx)
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

        imgs = tools.get_imgs('otros', id, cx)
        vals = tools.get_vals('otros', id, cx)
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
# Configuración adicional
#############################################


app.add_url_rule("/last_update/<type>", 'get_last_update',
                 upd.get_last_update)
app.add_url_rule("/last_update/<type>/<id>", 'get_last_update',
                 upd.get_last_update)
app.add_url_rule("/update/<type>", 'modify_last_update',
                 upd.modify_last_update)
app.add_url_rule("/update/<type>/<id>", 'modify_last_update',
                 upd.modify_last_update)


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
