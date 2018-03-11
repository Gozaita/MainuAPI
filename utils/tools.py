# -*- coding: utf-8 -*-
from flask import request
import logging

SRV_PATH = 'https://server.mainu.eus/'
IMG_PATH = SRV_PATH + 'external/images/'
BOC_PATH = IMG_PATH + 'bocadillos/'
PLT_PATH = IMG_PATH + 'platos/'
OTH_PATH = IMG_PATH + 'otros/'

logger = logging.getLogger(__name__)


def get_imgs(type, id, cx):
    """
    Devuelve todas las imágenes asociadas a un elemento con un <id> del
    tipo <type> que se especifique. La primera imagen de la lista es la
    marcada como 'oficial'.
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
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return None


def get_vals(type, id, cx):
    """
    Devuelve todas las valoraciones asociadas a un elemento con un <id> del
    tipo <type> que se especifique.
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
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return None


def get_ings(id, cx):
    """
    Devuelve todos los ingredientes asociados al bocadillo con el <id>
    especificado.
    """
    try:
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
        logger.exception("IP: %s\n" % request.environ['REMOTE_ADDR'] +
                         "Ha ocurrido una excepción durante la petición")
        return None
