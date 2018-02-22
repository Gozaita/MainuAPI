# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from sqlalchemy import create_engine
from time import localtime, strftime
import os
import sys
import logging

URI = open('.mainudb', 'r').read()
LOG_PATH = 'log/mainu.log'

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
            ing_ids = cx.execute("SELECT * FROM IngredienteBocadillo " +
                                 "WHERE Bocadillo_id=%d" % b['id'])
            ing = []
            for i in ing_ids:
                ing_lst = cx.execute("SELECT * FROM Ingrediente WHERE " +
                                     "Ingrediente.id=%d" % i['Ingrediente_id'])
                for i in ing_lst:
                    ing.append(i['nombre'])
            boc = {'id': b['id'], 'nombre': b['nombre'], 'precio': b['precio'],
                   'puntuacion': b['puntuacion'], 'ingredientes': ing}
            bocs_final.append(boc)
        return jsonify(bocs_final)
    except Exception as e:
        logging.exception("No se ha podido realizar la petición")
        return None


def fetch_menu():
        cx = db.connect()
        return cx.execute("SELECT * FROM Plato WHERE actual=True")


@app.route("/get_menu", methods=["GET"])
def get_menu():
    logging.info("Devolviendo menú del día...")
    try:
        query = fetch_menu()
        return jsonify([dict(zip(query.keys(), i))
                       for i in query.cursor.fetchall()])
    except Exception as e:
        logging.exception("No se ha podido realizar la petición")
        return None


@app.route("/get_menu_summary", methods=["GET"])
def get_menu_summary():
    logging.info("Devolviendo primeros del menú del día...")
    try:
        menu = fetch_menu()
        pr = []
        sg = []
        for p in menu:
            if p['tipo'] == 1:
                pr.append(p['nombre'])
            elif p['tipo'] == 2:
                sg.append(p['nombre'])
            else:
                ps = p['nombre']
        return jsonify({'primeros': pr, 'segundos': sg, 'postre': ps})
    except Exception as e:
        logging.exception("No se ha podido realizar la petición")
        return None


if __name__ == '__main__':
    app.run()
