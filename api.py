# -*- coding: utf-8 -*-
from flask import Flask, jsonify, redirect, request
from sqlalchemy import create_engine
from time import localtime, strftime
from logging.handlers import TimedRotatingFileHandler
import os
import logging

URI = open('.mainudb', 'r').read()
LOG_PATH = 'log/mainu.log'

SRV_PATH = 'https://server.mainu.eus/'
IMG_PATH = SRV_PATH + 'external/images/'
BOC_PATH = IMG_PATH + 'bocadillos/'
PLT_PATH = IMG_PATH + 'platos/'
OTH_PATH = IMG_PATH + 'otros/'

API_MAIN = "https://www.mainu.eus/api"

db = create_engine(URI)
app = Flask(__name__)

#############################################
# MainU Logger
#############################################


def log_setup():
    try:
        log = open(LOG_PATH, 'a')
    except FileNotFoundError:
        if not os.path.exists(os.path.dirname(LOG_PATH)):
            os.makedirs(os.path.dirname(LOG_PATH))
        log = open(LOG_PATH, 'w')

    log.write("##############################################\n")
    log.write("MainU -- mainu.eus -- %s\n"
              % strftime("%Y-%m-%d %H:%M:%S", localtime()))
    log.write("API REST\n")
    log.write("##############################################\n")
    log.close()

    handler = TimedRotatingFileHandler(LOG_PATH,
                                       when="d",
                                       interval=1,
                                       backupCount=7)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s]: %(levelname)s - ' +
                                  '%(funcName)s - %(message)s')
    handler.setFormatter(formatter)
    return handler


#############################################
# MainU API
#############################################


@app.route("/get_bocadillos", methods=["GET"])
def get_bocadillos():
    app.logger.info("Devuelve lista completa de los bocadillos disponibles")
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
        app.logger.exception("Ha ocurrido una excepción durante la petición")
        return None


@app.route("/get_menu", methods=["GET"])
def get_menu():
    app.logger.info("Devuelve menú del día actualizado")
    try:
        cx = db.connect()
        menu = cx.execute("SELECT * FROM Plato WHERE actual=True")
        pr = []
        sg = []
        ps = []
        for p in menu:
            app.logger.debug("Plato %d" % p['id'])
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
        app.logger.exception("Ha ocurrido una excepción durante la petición")
        return None


@app.route("/get_otros", methods=["GET"])
def get_otros():
    app.logger.info("Devuelve otros elementos")
    try:
        cx = db.connect()
        otros = cx.execute("SELECT * FROM Otro")
        otros_final = []
        for o in otros:
            app.logger.debug("Otro %d" % o['id'])
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
        app.logger.exception("Ha ocurrido una excepción durante la petición")
        return None


@app.route("/get_bocadillo", methods=["GET"])
def get_bocadillo():
    try:
        app.logger.info("Devuelve bocadillo: id %s" % request.args.get('id'))
        id = int(request.args.get('id'))
    except Exception:
        app.logger.exception("Excepción inicial")
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
        app.logger.exception("Ha ocurrido una excepción durante la petición")
        return None


@app.route("/get_plato", methods=["GET"])
def get_plato():
    app.logger.info("Devuelve plato: id %s" % request.args.get('id'))
    id = int(request.args.get('id'))
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
        app.logger.exception("Ha ocurrido una excepción durante la petición")
        return None


@app.route("/", methods=["GET"])
def api_main():
    app.logger.info("Redirige a %s" % API_MAIN)
    return redirect(API_MAIN)


if __name__ == '__main__':
    handler = log_setup()
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)
    app.run()
