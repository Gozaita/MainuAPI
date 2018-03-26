# -*- coding: utf-8 -*-
from flask import Flask, jsonify, redirect, request, render_template
from flask_httpauth import HTTPBasicAuth
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from utils import config, updates, usuarios, bocadillos, imagenes, valoraciones
from utils import logger as log
import logging

logger = logging.getLogger(__name__)

handler = log.get_handler()
app = Flask(__name__)
auth = HTTPBasicAuth()
app.logger.addHandler(handler)
app.logger.setLevel(logging.DEBUG)

updates.init()

user, pswd, host, schm = config.get_database()
HTTP_USERS = config.get_httpauth()
API_MAIN = config.get('PATH', 'api')

db = create_engine('mysql://%s:%s@%s/%s' % (user, pswd, host, schm))


@auth.get_password
def get_pw(username):
    if username in HTTP_USERS:
        return HTTP_USERS.get(username)
    return None


@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(405)
def bad_method(e):
    return render_template('405.html'), 405


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

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

@app.route('/add_valoracion/<type>/<int:id>', methods=['POST'])
def add_val(type, id):
    """
    Añade una nueva valoración del tipo <type> (bocadillos, menu, otros). Debe
    recibir en formato JSON el idToken y el objeto Valoracion (NO se le pasar
    el id del usuario dentro de este objeto, el usuario queda identificado
    a través del idToken).
    """
    logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                "Añade una valoración en: %s, %d" % (type, id))
    try:
        cx = db.connect()
        data = request.get_json(silent=True)
        idToken = data['idToken']
        valoracion = data['valoracion']
        usuario = usuarios.verify_token(idToken)
        if usuario is not None:
            u = usuarios.user_exists(usuario['id'], cx)
            if u is not None:
                # TODO: Actualizar datos de la BD si son diferentes (foto...)
                val = valoraciones.get_val(type, id, usuario['id'], cx)
                if val is not None:
                    logger.warning("Ya existe una valoración del usuario " +
                                   "para este elemento.")
                    return render_template('400.html', expl=config.VAL_EX), 400
                r = valoraciones.new_val(type, id, valoracion, usuario['id'],
                                         cx)
                return jsonify(r)
            else:
                r = usuarios.add_user(usuario['id'], usuario['nombre'],
                                      usuario['mail'], usuario['foto'], cx)
                if r is not None:
                    r = valoraciones.new_val(type, id, valoracion,
                                             usuario['id'], cx)
                    return jsonify(r)
                else:
                    logger.warning("No se ha podido añadir el usuario")
                    return render_template('500.html', errcode='USR.ADD'), 500
        else:
            logger.warning("El usuario no ha podido ser verificado")
            return render_template('400.html', expl=config.BAD_IDTOKEN), 400
    except OperationalError:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido un error con la base de datos")
        return render_template('500.html', errcode='SQL'), 500
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return render_template('500.html'), 500


@app.route("/valoracion/<type>/<int:id>", methods=["POST"])
def get_val(type, id):
    """
    Devuelve la valoración de un usuario para el elemento dado, en caso
    de que exista. Si no existe, devuelve False.
    """
    logger.debug("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                 "Solicita valoración de usuario: %s, %d" % (type, id))
    try:
        cx = db.connect()
        data = request.get_json(silent=True)
        idToken = data['idToken']
        usuario = usuarios.verify_token(idToken)
        if usuario is not None:
            v = valoraciones.get_val(type, id, usuario['id'], cx)
            if v is None:
                logger.debug("No existe valoración de usuario")
                return jsonify(False)
            else:
                logger.debug("El usuario ya ha valorado este producto")
                return jsonify(v)
        else:
            logger.warning("El usuario no ha podido ser verificado")
            return render_template('400.html', expl=config.BAD_IDTOKEN), 400
    except OperationalError:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido un error con la base de datos")
        return render_template('500.html', errcode='SQL'), 500
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return render_template('500.html'), 500


@app.route("/valoraciones/<type>", methods=["GET"])
@auth.login_required
def get_invisible_vals(type):
    """
    Devuelve todas las valoraciones ocultas para elementos del <type>
    especificado.
    """
    logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                "Devuelve valoraciones ocultas: %s" % type)
    try:
        cx = db.connect()
        r = valoraciones.get_invisible_vals(type, cx)
        cx.close
        if r is None:
            return render_template('500.html', errcode='VAL.GET_INV_VALS'), 500
        elif r is False:
            return render_template('400.html', expl=config.BAD_TYPE), 400
        return jsonify(r)
    except OperationalError:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido un error con la base de datos")
        return render_template('500.html', errcode='SQL'), 500
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return render_template('500.html'), 500


@app.route("/update_val/<type>/<int:id>", methods=["GET"])
@auth.login_required
def update_val(type, id):
    """
    Cambia el estado de una valoración con <id> especificado del <type>
    que se indique. Se le debe pasar como argumento la acción (action), que
    podrá tomar los valores 'visible' o 'delete'.
    """
    logger.info("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                "Actualiza estado de valoración: %s, %d" % (type, id))
    try:
        action = request.args.get('action', default=None)
        if action is None:
            logger.warning("No se ha pasado una acción como parámetro")
            return render_template('400.html', expl=config.BAD_ACTION), 400
        elif action != 'visible' and action != 'delete':
            logger.warning("La acción que se ha pasado no es válida")
            return render_template('400.html', expl=config.BAD_ACTION), 400
        cx = db.connect()
        r = valoraciones.update_val(type, id, action, cx)
        if r is None:
            return render_template('500.html', errcode='VAL.UPDATE_VAL'), 500
        elif r is False:
            return render_template('400.html', expl=config.BAD_TYPE), 400
        cx.close
        return jsonify(r)
    except OperationalError:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido un error con la base de datos")
        return render_template('500.html', errcode='SQL'), 500
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return render_template('500.html'), 500

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
    except OperationalError:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido un error con la base de datos")
        return render_template('500.html', errcode='SQL'), 500
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return render_template('500.html'), 500


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
    except OperationalError:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido un error con la base de datos")
        return render_template('500.html', errcode='SQL'), 500
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return render_template('500.html'), 500


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
        if b is None:
            return render_template('400.html', expl=config.BAD_ID), 400
        else:
            boc = {'id': b['id'], 'nombre': b['nombre'], 'precio': b['precio'],
                   'puntuacion': b['puntuacion'], 'ingredientes': ings,
                   'images': imgs, 'valoraciones': vals}
            return jsonify(boc)
    except OperationalError:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido un error con la base de datos")
        return render_template('500.html', errcode='SQL'), 500
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return render_template('500.html'), 500

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
    except OperationalError:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido un error con la base de datos")
        return render_template('500.html', errcode='SQL'), 500
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return render_template('500.html'), 500


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
        if p is None:
            return render_template('400.html', expl=config.BAD_ID), 400
        else:
            plt = {'id': p['id'], 'nombre': p['nombre'], 'puntuacion':
                   p['puntuacion'], 'descripcion': p['descripcion'],
                   'tipo': p['tipo'], 'images': imgs, 'valoraciones': vals}
            return jsonify(plt)
    except OperationalError:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido un error con la base de datos")
        return render_template('500.html', errcode='SQL'), 500
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return render_template('500.html'), 500

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
                    o['precio'], 'puntuacion': o['puntuacion'],
                    'tipo': o['tipo'], 'images': imgs}
            otros_final.append(otro)
        cx.close()
        return jsonify(otros_final)
    except OperationalError:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido un error con la base de datos")
        return render_template('500.html', errcode='SQL'), 500
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return render_template('500.html'), 500


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
        if o is None:
            return render_template('400.html', expl=config.BAD_ID), 400
        else:
            otr = {'id': o['id'], 'nombre': o['nombre'], 'puntuacion':
                   o['puntuacion'], 'precio': o['precio'], 'images': imgs,
                   'tipo': o['tipo'], 'valoraciones': vals}
            return jsonify(otr)
    except OperationalError:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido un error con la base de datos")
        return render_template('500.html', errcode='SQL'), 500
    except Exception:
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return render_template('500.html'), 500

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
    logger.debug("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                 "Devuelve última fecha de modificación")

    r = updates.get_last_update(type, id)

    if not r:
        return render_template("400.html", expl=config.BAD_TYPE_ID), 400
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
    logger.debug("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                 "Actualiza la última fecha de modificación")

    r = updates.modify_last_update(type, id)

    if r is False:
        return render_template("400.html", expl=config.BAD_TYPE), 400
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
