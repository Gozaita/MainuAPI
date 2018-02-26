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

Documentación
-------------

La API se encuentra disponible en [api.mainu.eus](https://api.mainu.eus). Puedes acceder a las diferentes funciones a través de dicha URL utilizando HTTPS.

### Funciones

#### get_bocadillos
**methods=[GET] query=[]**

Devuelve la lista de bocadillos en formato `JSON`. No necesita ningún parámetro. Cada elemento tiene la estructura de la [versión resumida de un objeto `Bocadillo`](#bocadillo).

#### get_menu
**methods=[GET] query=[]**

Devuelve el menú del día en formato `JSON`. No necesita ningún parámetro. Consiste en un diccionario de tres listas:
```
{
  "postre": [...],
  "primeros": [...],
  "segundos": [...]
}
```
Por lo general, el postre sólo contendrá un elemento, pero se devuelve igualmente una lista, como en los otros dos casos. Cada elemento dentro de estas listas tiene la estructura de la [versión resumida de un objeto `Plato`](#plato).

#### get_otros
**methods=[GET] query=[]**

Devuelve la lista de otros productos (bebidas, raciones...) en formato `JSON`. No necesita ningún parámetro. Cada elemento dentro de estas listas tiene la estructura de la [versión resumida de un objeto `Otro`](#otro).

#### get_bocadillo
**methods=[GET] query=[id]**

Devuelve la información asociada a un bocadillo en formato `JSON`. Se le ha de pasar como parámetro el `id` del bocadillo que se quiere solicitar (en caso de no pasarle este parámetro o de pasarle un `id` inexistente, se devolverá un error). La estructura que se devuelve es la correspondiente a un objeto [`Bocadillo`](#bocadillo).

#### get_plato
**methods=[GET] query=[id]**

Devuelve la información asociada a un plato en formato `JSON`. Se le ha de pasar como parámetro el `id` del plato que se quiere solicitar (en caso de no pasarle este parámetro o de pasarle un `id` inexistente, se devolverá un error). La estructura que se devuelve es la correspondiente a un objeto [`Plato`](#plato).

### Objetos

#### Bocadillo
```
{
  "id": 1,
  "imagen": null,
  "ingredientes": [
    "bacon"
  ],
  "nombre": "Bacon",
  "precio": 2.05,
  "puntuacion": null,
  "valoraciones": [...]
}
```

- `id` es el identificador del bocadillo (uso interno).

- `imagen` es la URL en la que se encuentra la imagen predeterminada para dicho bocadillo. Si no existe una imagen considerada *oficial* para un bocadillo, el campo podrá ser `null`

- `ingredientes` es la lista de ingredientes que tiene el bocadillo.

- `nombre` es el nombre del bocadillo en castellano.

- `precio` indica el precio del bocadillo.

- `puntuacion` es la media de la puntuación obtenida en las valoraciones. Si no hay puntuaciones con las que hacer la media, su valor será `null`.

- `valoraciones` es una lista de las valoraciones enviadas y aprobadas para dicho bocadillo. La estructura de cada elemento se corresponde con la del objeto [`Valoración`](#valoracion).

##### Versión resumida
```
{
  "id": 6,
  "ingredientes": [
    "bacon",
    "queso",
    "huevo",
    "pollo"
  ],
  "nombre": "Jamaika",
  "precio": 3.55,
  "puntuacion": null
}
```

- `id` es el identificador del bocadillo (uso interno).

- `ingredientes` es la lista de ingredientes que tiene el bocadillo.

- `nombre` es el nombre del bocadillo en castellano.

- `precio` indica el precio del bocadillo.

- `puntuacion` es la media de la puntuación obtenida en las valoraciones. Si no hay puntuaciones con las que hacer la media, su valor será `null`.

#### Plato
```
{
  "descripcion": null,
  "id": 1,
  "imagen": "https://server.mainu.eus/external/images/platos/1_2018-01-01--00-00-00-000.jpg",
  "nombre": "Huevos gratinados",
  "puntuacion": null,
  "tipo": 1,
  "valoraciones": [...]
}
```

- `descripcion` es una descripción breve del plato. Puede no existir y, por lo tanto, devolver el valor `null`.

- `id` es el identificador del bocadillo (uso interno).

- `imagen` es la URL en la que se encuentra la imagen predeterminada para dicho plato. Si no existe una imagen considerada *oficial* para un plato, el campo podrá ser `null`

- `nombre` es el nombre del plato en castellano.

- `precio` indica el precio del bocadillo.

- `puntuacion` es la media de la puntuación obtenida en las valoraciones. Si no hay puntuaciones con las que hacer la media, su valor será `null`.

- `tipo` indica el tipo de plato que es: primero (1), segundo (2) o postre (3).

- `valoraciones` es una lista de las valoraciones enviadas y aprobadas para dicho plato. La estructura de cada elemento se corresponde con la del objeto [`Valoración`](#valoracion).

##### Versión resumida
```
{
  "id": 6,
  "imagen": "https://server.mainu.eus/external/images/platos/6_2018-01-01--00-00-00-000.jpg",
  "nombre": "Ensalada de pasta",
  "puntuacion": null
}
```
- `id` es el identificador del plato (uso interno).

- `imagen` es la URL en la que se encuentra la imagen predeterminada para dicho plato. Si no existe una imagen considerada *oficial* para un plato, el campo podrá ser `null`.

- `nombre` es el nombre del plato en castellano.

- `puntuacion` es la media de la puntuación obtenida en las valoraciones. Si no hay puntuaciones con las que hacer la media, su valor será `null`.

#### Otro

##### Versión resumida
```
{
  "id": 1,
  "imagen": null,
  "nombre": "Fanta",
  "precio": 1.00,
  "puntuacion": null
}
```

- `id` es el identificador del producto (uso interno).

- `imagen` es la URL en la que se encuentra la imagen predeterminada para dicho producto. Si no existe una imagen considerada *oficial* para un producto, el campo podrá ser `null`.

- `nombre` es el nombre del producto en castellano.

- `precio` indica el precio del producto.

- `puntuacion` es la media de la puntuación obtenida en las valoraciones. Si no hay puntuaciones con las que hacer la media, su valor será `null`.


#### Valoración

Las valoraciones son enviadas por la API en las funciones `get_bocadillo`, `get_plato` y `get_otro`. Estas funciones devuelven, entre otros datos, una lista con valoraciones. A pesar de ser valoraciones de diferentes objetos, todas tienen la misma estructura:
```
{
  "foto": "https://i.imgur.com/Wc9VOaZ.png",
  "id": 1,
  "nombre": "Mainu Team",
  "puntuacion": 3,
  "texto": "Esta es una valoraci\u00f3n de prueba. El usuario puede escribir hasta 280 caracteres."
}
```
