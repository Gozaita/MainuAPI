# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


def get_ings_by_id(id, cx):
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
        logger.exception("Ha ocurrido una excepción durante la petición")
        return None


def get_ings_all(cx):
    ins = cx.execute("SELECT * FROM Ingrediente")

    ings = []

    for i in ins:
        ings.append({'id': i['id'], 'nombre': i['nombre']})
    return ings
