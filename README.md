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

### `/get_bocadillos` `[GET]`

Devuelve un `array` en formato `JSON` de la lista de bocadillos, donde cada elemento tiene el siguiente formato:
```
{
  "id": 1,
  "ingredientes": [
    "Pechuga",
    "Lechuga",
    "Tomate"
  ],
  "nombre": "Ave César",
  "precio": 2.50,
  "puntuacion": 7.8
}
```

- `id` es el identificador del bocadillo (uso interno).

- `ingredientes` es la lista de ingredientes que tiene el bocadillo.

- `nombre` es el nombre del bocadillo en castellano.

- `precio` indica el precio del bocadillo.

- `puntuacion` es la media de la puntuación obtenida en las valoraciones.

### `/get_menu` `[GET]`

Devuelve un `array` en formato `JSON` del menú del día (por lo general: tres primeros, tres segundos y un postre), donde cada elemento tiene el siguiente formato:
```
{
  "actual": 1,
  "descripcion": null,
  "id": 2,
  "izena": null,
  "nombre": "Plato2",
  "tipo": 1
}
```
- `actual` indica si el plato se encuentra en el menú del día o no.

- `descripcion` permite introducir una descripción del plato.

- `id` es el identificador del plato (uso interno).

- `izena` es el nombre del plato en euskera.

- `nombre` es el nombre del plato en castellano.

- `tipo` indica si es un primero (1), segundo (2) o un postre (3).

### `/get_menu_summary` `[GET]`

Devuelve un *diccionario* en formato `JSON` con los nombres de los platos del menú del día:
```
{
  "postre": "Plato7",
  "primeros": [
    "Plato2",
    "Plato4",
    "Plato10"
  ],
  "segundos": [
    "Plato5",
    "Plato8",
    "Plato11"
  ]
}
```
- `postre` incluye un único elemento, correspondiente al campo `nombre` del postre que se encuentre en el menú del día.

- `primeros` incluye un `array` de los campos `nombre` de los primeros que se encuentren en el menú del día.

- `segundos` incluye un `array` de los campos `nombre` de los segundos que se encuentren en el menú del día.

> *En desarrollo...*
