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

#### /bocadillos
**methods=[GET]**

Devuelve la lista de bocadillos en formato `JSON`. No necesita ningún parámetro. Cada elemento tiene la estructura de la [versión resumida de un objeto `Bocadillo`](#bocadillo).

#### /bocadillos/\<id\>
**methods=[GET] parámetros=[id]**

Devuelve la información asociada a un bocadillo en formato `JSON`. Se le ha de pasar como parámetro el `id` del bocadillo que se quiere solicitar (en caso de no pasarle este parámetro o de pasarle un `id` inexistente, se devolverá un error). La estructura que se devuelve es la correspondiente a un objeto [`Bocadillo`](#bocadillo).

#### /menu
**methods=[GET]**

Devuelve el menú del día en formato `JSON`. No necesita ningún parámetro. Consiste en un diccionario de tres listas:
```
{
  "postre": [...],
  "primeros": [...],
  "segundos": [...]
}
```
Por lo general, el postre sólo contendrá un elemento, pero se devuelve igualmente una lista, como en los otros dos casos. Cada elemento dentro de estas listas tiene la estructura de la [versión resumida de un objeto `Plato`](#plato).

#### /menu/\<id\>
**methods=[GET] parámetros=[id]**

Devuelve la información asociada a un plato en formato `JSON`. Se le ha de pasar como parámetro el `id` del plato que se quiere solicitar (en caso de no pasarle este parámetro o de pasarle un `id` inexistente, se devolverá un error). La estructura que se devuelve es la correspondiente a un objeto [`Plato`](#plato).

#### /otros
**methods=[GET]**

Devuelve la lista de otros productos (bebidas, raciones...) en formato `JSON`. No necesita ningún parámetro. Cada elemento dentro de estas listas tiene la estructura de la [versión resumida de un objeto `Otro`](#otro).

#### /otros/\<id\>
**methods=[GET] parámetros=[id]**

Devuelve la información asociada a un producto de la categoría *Otros* en formato `JSON`. Se le ha de pasar como parámetro el `id` del producto que se quiere solicitar (en caso de no pasarle este parámetro o de pasarle un `id` inexistente, se devolverá un error). La estructura que se devuelve es la correspondiente a un objeto [`Otro`](#otro).

### Objetos

Para algunos objetos se detallan versiones resumidas de los mismos. Estas versiones reflejan los datos devueltos por algunas funciones que no tienen en cuenta todos los atributos.

#### Bocadillo
```
{
  "id": 6,
  "images": [...],
  "ingredientes": [...],
  "nombre": "Jamaika",
  "precio": 3.55,
  "puntuacion": null,
  "valoraciones": [...]
}
```

- `id` es el identificador del bocadillo (uso interno).

- `images` es una lista de elementos tipo [`Imagen`](#imagen) correspondientes al bocadillo. Muestra únicamente las imágenes marcadas como visibles. Esta lista puede estar vacía si no hay ninguna imagen para el elemento. La primera imagen de la lista será la oficial.

- `ingredientes` es la lista de elementos tipo [`Ingrediente`](#ingrediente) correspondientes al bocadillo.

- `nombre` es el nombre del bocadillo en castellano.

- `precio` indica el precio del bocadillo.

- `puntuacion` es la media de la puntuación obtenida en las valoraciones. Si no hay puntuaciones con las que hacer la media, su valor será `null`.

- `valoraciones` es una lista de las valoraciones enviadas y aprobadas para dicho bocadillo. La estructura de cada elemento se corresponde con la del objeto [`Valoración`](#valoración). Esta lista puede estar vacía si no hay ninguna valoración para el elemento.

##### Versión resumida
```
{
  "id": 1,
  "ingredientes": [...],
  "nombre": "Bacon",
  "precio": 2.05,
  "puntuacion": null
}
```

#### Plato
```
{
  "descripcion": null,
  "id": 4,
  "images": [...],
  "nombre": "Albóndigas con tomate",
  "puntuacion": null,
  "tipo": 2,
  "valoraciones": [...]
}
```

- `descripcion` es una descripción breve del plato. Puede no existir y, por lo tanto, devolver el valor `null`.

- `id` es el identificador del plato (uso interno).

- `images` es una lista de elementos tipo [`Imagen`](#imagen) correspondientes al plato. Muestra únicamente las imágenes marcadas como visibles. Esta lista puede estar vacía si no hay ninguna imagen para el elemento. La primera imagen de la lista será la oficial.

- `nombre` es el nombre del plato en castellano.

- `precio` indica el precio del bocadillo.

- `puntuacion` es la media de la puntuación obtenida en las valoraciones. Si no hay puntuaciones con las que hacer la media, su valor será `null`.

- `tipo` indica el tipo de plato que es: primero (1), segundo (2) o postre (3).

- `valoraciones` es una lista de las valoraciones enviadas y aprobadas para dicho plato. La estructura de cada elemento se corresponde con la del objeto [`Valoración`](#valoracion). Esta lista puede estar vacía si no hay ninguna valoración para el elemento.

##### Versión resumida
```
{
  "id": 3,
  "images": [...],
  "nombre": "Fruta",
  "puntuacion": null
}
```
> **Nota**: en este caso, la lista `images` contiene un único elemento, la imagen oficial para el plato (en caso de existir).

#### Otro
```
{
  "id": 4,
  "images": [...],
  "nombre": "Bocadillo de Calamares",
  "precio": 2.90,
  "puntuacion": null,
  "valoraciones": [...]
}
```

- `id` es el identificador del producto (uso interno).

- `images` es una lista de elementos tipo [`Imagen`](#imagen) correspondientes al producto. Muestra únicamente las imágenes marcadas como visibles. Esta lista puede estar vacía si no hay ninguna imagen para el elemento. La primera imagen de la lista será la oficial.

- `nombre` es el nombre del producto en castellano.

- `precio` indica el precio del producto.

- `puntuacion` es la media de la puntuación obtenida en las valoraciones. Si no hay puntuaciones con las que hacer la media, su valor será `null`.

- `valoraciones` es una lista de las valoraciones enviadas y aprobadas para dicho producto. La estructura de cada elemento se corresponde con la del objeto [`Valoración`](#valoracion). Esta lista puede estar vacía si no hay ninguna valoración para el elemento.

##### Versión resumida
```
{
  "id": 1,
  "images": [...],
  "nombre": "Fanta",
  "precio": 1.00,
  "puntuacion": null
}
```
> **Nota**: en este caso, la lista `images` contiene un único elemento, la imagen oficial para el plato (en caso de existir).

#### Imagen
```
{
  "id": 7,
  "url": "https://server.mainu.eus/external/images/platos/7_2018-01-01--00-00-00-000.jpg"
}
```

- `id` es el identificador de la imagen (uso interno).

- `url` es la URL en la que se encuentra la imagen en cuestión.

#### Ingrediente
```
{
  "id": 9,
  "nombre": "bacon"
}
```

- `id` es el identificador del ingrediente (uso interno).

- `nombre` es el nombre en castellano del ingrediente.

#### Valoración
```
{
  "id": 1,
  "puntuacion": 4,
  "texto": "Delicioso bocadillo, aunque echo en falta alguna salsa que lo acompañe.",
  "usuario": {...}
}
```

- `id` es el identificador de la valoración (uso interno).

- `puntuacion` es la puntuación otorgada por el autor o autora de la valoración.

- `texto` es el comentario opcional que el usuario puede añadir al enviar una valoración. Es un campo opcional, por lo que puede ser `null`.

- `usuario` contiene la información del usuario que ha realizado la valoración, en un objeto de tipo [`Usuario`](#usuario).

#### Usuario
```
{
  "foto": "https://i.imgur.com/Wc9VOaZ.png",
  "id": "0",
  "nombre": "Mainu Team",
  "verificado": 1
}
```

- `foto` es la URL donde se encuentra la foto de perfil del usuario.

- `id` es el identificador del usuario (uso interno).

- `nombre` es el nombre completo del usuario.

- `verificado` indica si es un usuario verificado o no.
