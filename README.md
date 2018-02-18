>*Este repositorio contiene la API del proyecto **MainU**. Para el cliente de Android, consulta [**MainU App**](https://github.com/Gozaita/MainuApp). Para una visión global del proyecto, puedes dirigirte a [mainu.eus](http://mainu.eus).*

<img src=https://i.imgur.com/Wc9VOaZ.png?1 width=150px/>

MainU API
===================

**MainU API** es la interfaz que permite la creación de aplicaciones y servicios a partir de la interacción con la base de datos de MainU. Su ámbito de actuación se centra en la Escuela de Ingeniería de Bilbao (UPV/EHU).

> Desarrollado por Ismael Estalayo, Guillermo Ozaita, Andreea Stanciu y Adrián Vázquez.
>
> +info: [mainu.eus](http://mainu.eus)

----------

El proyecto de MainU
-------------

**MainU** es un proyecto que pretende dar servicio al alumnado y profesorado de la Escuela de Ingeniería de Bilbao así como al resto de público objetivo de la cafetería del centro. El proyecto engloba diferentes partes:
- Base de datos de MainU
- [MainU API](https://github.com/Gozaita/MainuAPI)
- [MainU App](https://github.com/Gozaita/MainuApp)

Dependencias
-------------

```
pip3 install sqlalchemy
pip3 install mysqlclient
pip3 install flask
pip3 install simplejson
```
La instalación de SQLAlchemy puede dar problemas en entornos Windows. Si se da el caso, descargar de la [web oficial](https://www.sqlalchemy.org/download.html), descomprimir e instalar usando `py setup.py install`.

Funciones ofrecidas por la API
-------------

La API REST que proporciona acceso a las diferentes funciones que aquí se muestran está accesible a través de **mainu.eus/api**. Junto a cada función se indican los métodos soportados (`GET`, `POST`).

- `/get_bocadillos` `[GET]`

Devuelve un `array` en formato `JSON`, donde cada elemento tiene el siguiente formato:
```
{
  "calorias": null,
  "id": 1,
  "izena": "Ave César",
  "nombre": "Ave César",
  "precio": 3.50
}
```
> *En desarrollo...*
