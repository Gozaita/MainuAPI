# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


def new_plato(nombre, tipo, cx):
    try:
        cx.execute("INSERT INTO Plato (nombre, tipo, actual) " +
                   "VALUE (\"%s\", %d, False)" % (nombre, int(tipo)))
        return True
    except Exception:
        logger.exception("Ha ocurrido una excepción durante la petición")
        return None


def update_menu(ids, cx):
    try:
        cx.execute("UPDATE Plato SET actual=False WHERE actual=True")

        for id in ids:
            cx.execute("UPDATE Plato SET actual=True WHERE id=%d" % int(id))
        return True
    except Exception:
        logger.exception("Ha ocurrido una excepción durante la petición")
        return None
