# -*- coding: utf-8 -*-
from utils import config
import logging

TRASH = config.get('PATH', 'root') + config.get('PATH', 'trash')

logger = logging.getLogger(__name__)


def update_punt(cl, vt, id, cx):
    """
    Crea una lista de todos las puntuaciones y calcula la media para luego
    actualizarlo en la tabla=vt, id=cl
    """
    logger.debug("Actualiza la puntuación")
    try:
        if vt == 'ValoracionBocadillo':
            tabla = 'Bocadillo'
        elif vt == 'ValoracionPlato':
            tabla = 'Plato'
        elif vt == 'ValoracionOtro':
            tabla = 'Otro'
        else:
            logger.error("El tipo que se ha pasado no es válido")
            return False

        vls = cx.execute("SELECT v.puntuacion FROM %s AS v " % vt +
                         "WHERE %s=%d" % (cl, id)).fetchall()
        if vls is not None:
            i = 0
            p = 0
            while(i < len(vls)):
                p = p + float(vls[i]['puntuacion'])
                i = i + 1
        punt = p / len(vls)
        cx.execute("UPDATE %s SET puntuacion=%f WHERE id=%d"
                   % (tabla, punt, id))
        logger.debug("Puntuación actualizada para (%s, %d): %f" % (tabla, id,
                                                                   punt))
        return True
    except Exception:
        logger.exception("Ha ocurrido una excepción")
        return None


def get_vals(type, id, cx):
    """
    Devuelve todas las valoraciones asociadas a un elemento con un <id> del
    tipo <type> que se especifique. Solo devuelve aquellas visibles.
    """
    logger.debug("Devuelve las valoraciones asociadas: %s, %d" % (type, id))
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
            logger.error("El tipo que se ha pasado no es válido")
            return False

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
        logger.exception("Ha ocurrido una excepción durante la petición")
        return None


def get_invisible_vals(type, cx):
    try:
        if type == 'bocadillos':
            vt = 'ValoracionBocadillo'
        elif type == 'menu':
            vt = 'ValoracionPlato'
        elif type == 'otros':
            vt = 'ValoracionOtro'
        else:
            logger.error("El tipo que se ha pasado no es válido")
            return False

        vls = cx.execute("SELECT v.id, v.puntuacion, v.texto, v.Usuario_id, " +
                         "u.nombre, u.foto, u.verificado FROM %s AS v " % vt +
                         "INNER JOIN Usuario AS u ON u.id=Usuario_id " +
                         "WHERE visible=False")
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
        logger.exception("Ha ocurrido una excepción durante la petición")
        return None


def append_vals(vals, type, cx):
        n_vals = get_invisible_vals(type, cx)
        for v in n_vals:
            v['type'] = type
            vals.append(v)
        return vals


def get_all_invisible_vals(cx):
    try:
        vals = []
        vals = append_vals(vals, 'bocadillos', cx)
        vals = append_vals(vals, 'menu', cx)
        vals = append_vals(vals, 'otros', cx)
        return vals
    except Exception:
        logger.exception("Ha ocurrido una excepción durante la petición")
        return None


def update_val(type, id, action, cx):
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
            logger.error("El tipo que se ha pasado no es válido")
            return False, None

        if action == 'visible':
            cx.execute("UPDATE %s SET visible=True WHERE id=%d" % (vt, id))
            obj = cx.execute("SELECT %s FROM %s WHERE id=%d"
                             % (cl, vt, id)).fetchone()
            update_punt(cl, vt, obj[cl], cx)
            logger.debug("La valoración se ha hecho visible")
            return True, obj[cl]
        elif action == 'delete':
            val = cx.execute("SELECT * FROM %s WHERE id=%d"
                             % (vt, id)).fetchone()
            v = open(TRASH + type + '_' + str(id), 'w')
            v.write("##############################################\n")
            v.write("%s, %d\n" % (type, id))
            v.write("%s\n" % val)
            v.write("##############################################\n")
            v.close()
            cx.execute("DELETE FROM %s WHERE id=%d" % (vt, id))
            logger.debug("La valoración se ha borrado")
            return True, None
        else:
            return False, None
    except Exception:
        logger.exception("Ha ocurrido una excepción durante la petición")
        return None, None


def get_val(type, id, userId, cx):
    """
    Devuelve la valoración de un usuario, si existe, para un elemento con el
    <id> dado y del <type> indicado.
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
            logger.error("El tipo que se ha pasado no es válido")
            return False

        v = cx.execute('SELECT id, puntuacion, texto FROM %s ' % vt +
                       'WHERE %s=%d ' % (cl, id) +
                       'AND Usuario_id=\"%s\"' % userId).fetchone()
        if v is None:
            return None
        else:
            val = {'id': v['id'], 'puntuacion': v['puntuacion'],
                   'texto': v['texto']}
            return val
    except Exception:
        logger.exception("Ha ocurrido una excepción durante la petición")
        return None


def new_val(type, id, valoracion, userId, cx):
    """
    Añade una nueva valoración y llama a la función que actualiza la puntuacion
    """
    # TODO: Cambiar visibilidad a False por defecto (en True para pruebas)
    # TODO: Visibilidad por defecto a True para usuarios verificados
    logger.debug("Añade una nueva valoración")
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
            logger.error("El tipo que se ha pasado no es válido")
            return False

        puntuacion = float(valoracion['puntuacion'])
        texto = valoracion.get('texto', None)

        if texto is not None:
            cx.execute("INSERT INTO %s " % vt +
                       "(puntuacion, texto, visible, Usuario_id, %s) " % cl +
                       "VALUE (%f, \"%s\", False, %s, %d)"
                       % (puntuacion, texto, userId, id))
        else:
            cx.execute("INSERT INTO %s " % vt +
                       "(puntuacion, visible, Usuario_id, %s) " % cl +
                       "VALUE (%f, False, %s, %d)"
                       % (puntuacion, userId, id))
        cx.close()
        logger.debug("La valoración se ha añadido")
        return True
    except Exception:
        logger.exception("Ha ocurrido una excepción durante la petición")
        return None
