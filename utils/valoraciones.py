# -*- coding: utf-8 -*-
import logging

ROOT = ''  # ${ROOT_PATH} for production mode

DEL_VALS = ''

logger = logging.getLogger(__name__)


def setup(r):
    global ROOT, DEL_VALS
    ROOT = r
    DEL_VALS = ROOT + 'deleted_vals/'
    logger.info("Se ha establecido el directorio DEL_VALS: %s" % DEL_VALS)


def get_vals(type, id, cx):
    """
    Devuelve todas las valoraciones asociadas a un elemento con un <id> del
    tipo <type> que se especifique. Solo devuelve aquellas visibles.
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
            raise Exception

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


def update_val(type, id, action, cx):
    try:
        if type == 'bocadillos':
            vt = 'ValoracionBocadillo'
        elif type == 'menu':
            vt = 'ValoracionPlato'
        elif type == 'otros':
            vt = 'ValoracionOtro'
        else:
            raise Exception

        if action == 'visible':
            cx.execute("UPDATE %s SET visible=True WHERE id=%d" % (vt, id))
            return True
        elif action == 'delete':
            val = cx.execute("SELECT * FROM %s WHERE id=%d"
                             % (vt, id)).fetchone()
            v = open(DEL_VALS + type + '_' + str(id), 'w')
            v.write("##############################################\n")
            v.write("%s, %d\n" % (type, id))
            v.write("%s\n" % val)
            v.write("##############################################\n")
            v.close()
            cx.execute("DELETE FROM %s WHERE id=%d" % (vt, id))
            return True
    except Exception:
        logger.exception("Ha ocurrido una excepción durante la petición")
        return None
