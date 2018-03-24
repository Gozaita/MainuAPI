# -*- coding: utf-8 -*-
from utils import config
import logging

SRV_PATH = config.get('IMAGES', 'server')
IMG_PATH = SRV_PATH + config.get('IMAGES', 'images')
BOC_PATH = IMG_PATH + config.get('IMAGES', 'bocadillos')
PLT_PATH = IMG_PATH + config.get('IMAGES', 'platos')
OTH_PATH = IMG_PATH + config.get('IMAGES', 'otros')

IMGW_PATH = config.get('IMAGES', 'path') + config.get('IMAGES', 'images')
BOCW_PATH = IMGW_PATH + config.get('IMAGES', 'bocadillos')
PLTW_PATH = IMGW_PATH + config.get('IMAGES', 'platos')
OTHW_PATH = IMGW_PATH + config.get('IMAGES', 'otros')

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
        logger.exception("Ha ocurrido una excepción durante la petición")
        return None
