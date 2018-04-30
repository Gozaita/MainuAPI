# -*- coding: utf-8 -*-
from utils import config
import logging
import base64
import time
import os

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


def get_invisible_imgs(type, cx):
    try:
        if type == 'bocadillos':
            ft = 'FotoBocadillo'
            path = BOC_PATH
        elif type == 'menu':
            ft = 'FotoPlato'
            path = PLT_PATH
        elif type == 'otros':
            ft = 'FotoOtro'
            path = OTH_PATH
        else:
            logger.error("El tipo que se ha pasado no es válido")
            return False

        ims = cx.execute("SELECT f.id, f.ruta, f.Usuario_id, " +
                         "u.nombre, u.foto, u.verificado FROM %s AS f " % ft +
                         "INNER JOIN Usuario AS u ON u.id=Usuario_id " +
                         "WHERE visible=False")
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


def append_imgs(imgs, type, cx):
        n_imgs = get_invisible_imgs(type, cx)
        for i in n_imgs:
            i['type'] = type
            imgs.append(i)
        return imgs


def get_all_invisible_imgs(cx):
    try:
        imgs = []
        imgs = append_imgs(imgs, 'bocadillos', cx)
        imgs = append_imgs(imgs, 'menu', cx)
        imgs = append_imgs(imgs, 'otros', cx)
        return imgs
    except Exception:
        logger.exception("Ha ocurrido una excepción durante la petición")
        return None


def update_img(type, id, action, cx):
    try:
        if type == 'bocadillos':
            ft = 'FotoBocadillo'
            cl = 'Bocadillo_id'
            path = BOCW_PATH
        elif type == 'menu':
            ft = 'FotoPlato'
            cl = 'Plato_id'
            path = PLTW_PATH
        elif type == 'otros':
            ft = 'FotoOtro'
            cl = 'Otro_id'
            path = OTHW_PATH
        else:
            logger.error("El tipo que se ha pasado no es válido")
            return False, None

        if action == 'visible':
            cx.execute("UPDATE %s SET visible=True WHERE id=%d" % (ft, id))
            logger.debug("La foto se ha hecho visible")
            obj = cx.execute("SELECT %s FROM %s WHERE id=%d"
                             % (cl, ft, id)).fetchone()
            return True, obj[cl]
        elif action == 'delete':
            ruta = cx.execute("SELECT ruta FROM %s WHERE id=%d"
                              % (ft, id)).fetchone()['ruta']
            cx.execute("DELETE FROM %s WHERE id=%d" % (ft, id))
            os.rename(path + ruta, 'del_' + path + ruta)
            logger.debug("La imagen se ha borrado de la base de datos")
            return True, None
        elif action == 'oficial':
            cx.execute("UPDATE %s SET oficial=False WHERE oficial=True " % ft +
                       "AND %s=%d" % (cl, id))
            cx.execute("UPDATE %s SET oficial=True WHERE id=%d" % (ft, id))
            logger.debug("La imagen se ha hecho oficial")
            obj = cx.execute("SELECT %s FROM %s WHERE id=%d"
                             % (cl, ft, id)).fetchone()
            return True, obj[cl]
        else:
            return False, None
    except Exception:
        logger.exception("Ha ocurrido una excepción durante la petición")
        return None, None


def crea_nombre(id):
    try:
        timestamp = time.strftime("%Y-%m-%d--%H-%M-%S")
        nombre = str(id)+'_'+timestamp
        return nombre
    except Exception:
        logger.exception("No se ha podido crear el nombre de la imagen")
        return None


def write_img(img, id, type):
    try:
        if type == 'bocadillos':
            path = BOCW_PATH
        elif type == 'menu':
            path = PLTW_PATH
        elif type == 'otros':
            path = OTHW_PATH
        else:
            raise Exception
        imagen = base64.decodebytes(img)
        nombre = crea_nombre(id) + '.jpg'
        f = open(path + nombre, "wb")
        f.write(imagen)
        f.close()
        logger.debug("La imagen se ha guardado con el nombre: %s" % nombre)
        return nombre
    except Exception:
        logger.exception("Ha ocurrido un error")
        return None


def update_db(id, type, nombre, cx, userId):
    try:
        if type == 'bocadillos':
            ft = 'FotoBocadillo'
            cl = 'Bocadillo_id'
        elif type == 'menu':
            ft = 'FotoPlato'
            cl = 'Plato_id'
        elif type == 'otros':
            ft = 'FotoOtro'
            cl = 'Otro_id'
        else:
            raise Exception
        cx.execute("INSERT INTO %s " % ft +
                   "(ruta, visible, oficial, %s, Usuario_id) " % cl +
                   "VALUE (\"%s\", False, True,  %d, \"%s\")"
                   % (nombre, id, userId))
        cx.close()
        logger.debug("La base de datos se ha actualizado correctamente")
        return True
    except Exception:
        logger.exception("Ha ocurrido un error")
        return None
