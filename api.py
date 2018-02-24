# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from sqlalchemy import create_engine
from time import localtime, strftime
import os
import sys
import logging

URI = open('.mainudb', 'r').read()
LOG_PATH = 'log/mainu.log'

SRV_PATH = 'https://www.mainu.eus/'
IMG_PATH = SRV_PATH + 'external/images/'
BOC_PATH = IMG_PATH + 'bocadillos/'
PLT_PATH = IMG_PATH + 'platos/'
OTH_PATH = IMG_PATH + 'otros/'

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

sys.stdout = open(LOG_PATH, 'a')
sys.stderr = sys.stdout

logging.basicConfig(filename=LOG_PATH,
                    format='[%(asctime)s]: %(levelname)s - ' +
                    '%(funcName)s - %(message)s',
                    filemode='a',
                    level=logging.DEBUG)

db = create_engine(URI)
app = Flask(__name__)

#############################################
# MainU API
#############################################


@app.route("/get_bocadillos", methods=["GET"])
def get_bocadillos():
    logging.info("Devolviendo lista de bocadillos...")
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
    except Exception as e:
        logging.exception("No se ha podido realizar la petición")
        return None


@app.route("/get_menu", methods=["GET"])
def get_menu():
    logging.info("Devolviendo menú del día...")
    try:
        cx = db.connect()
        menu = cx.execute("SELECT * FROM Plato WHERE actual=True")
        pr = []
        sg = []
        for p in menu:
            logging.debug("Plato %d" % p['id'])
            im = cx.execute("SELECT FotoPlato.ruta FROM FotoPlato WHERE " +
                            "FotoPlato.Plato_id=%d AND " % p['id'] +
                            "FotoPlato.oficial=True").fetchone()
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
                ps = pl
        return jsonify({'primeros': pr, 'segundos': sg, 'postre': ps})
    except Exception as e:
        logging.exception("No se ha podido realizar la petición")
        return None


if __name__ == '__main__':
    app.run()
