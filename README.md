# Sistema de gestión de inventario para tienda de ropa, calzado y accesorios

## 1. Objetivo del sistema

Este proyecto fue desarrollado como una aplicación web para gestionar el inventario de una pequeña tienda que vende ropa, calzado y accesorios. La aplicación está pensada para ser usada por la administradora de la tienda, no por clientes.

El objetivo principal es registrar productos, manejar variantes por talla y color, consultar existencias y mantener un historial de movimientos de inventario de forma sencilla y ordenada.

## 2. Problema que resuelve

En una tienda pequeña, es común que el inventario se maneje de manera manual y sin un control claro. Esto puede provocar:

- pérdida de información sobre productos y variantes
- errores al registrar stock
- dificultad para saber cuántas unidades hay disponibles
- falta de control de entradas y salidas
- dificultad para identificar productos con stock bajo

Este sistema ayuda a registrar y consultar la información de forma centralizada, usando SQLite como base de datos local y Flask como servidor web.

## 3. Funcionalidades reales implementadas

La versión actual del proyecto incluye las siguientes funcionalidades:

### 3.1 Registro de productos
La aplicación permite registrar un producto con:

- nombre
- categoría
- descripción
- precio

Cada producto queda guardado en la base de datos.

### 3.2 Registro de variantes
Cada producto puede tener varias variantes según talla y color. Para cada variante se guarda:

- producto asociado
- talla
- color
- cantidad inicial
- stock mínimo

La cantidad inicial se guarda como stock actual y además se registra un movimiento inicial de tipo "inicial" para dejar constancia del stock existente.

### 3.3 Consulta del inventario
La aplicación muestra una vista de inventario con:

- nombre del producto
- categoría
- talla
- color
- stock actual
- stock mínimo
- estado de alerta si el stock está igual o por debajo del mínimo

### 3.4 Registro de movimientos
La aplicación permite registrar movimientos de inventario:

- entrada: aumenta las existencias
- salida: disminuye las existencias

Durante la operación se valida que la salida no supere la cantidad disponible.

### 3.5 Historial de movimientos
La aplicación mantiene un historial con:

- fecha
- producto
- variante
- tipo de movimiento
- cantidad
- motivo

### 3.6 Alertas por stock bajo
Cuando la cantidad disponible de una variante es igual o menor que el stock mínimo configurado, la app marca una alerta en la sección de inventario.

### 3.7 Ruta JSON de productos
La aplicación expone una ruta JSON para consultar los productos registrados:

- /api/productos

Esta ruta devuelve una estructura JSON con los datos esenciales de los productos y sus variantes.

## 4. Tecnologías utilizadas

Se utiliza únicamente el stack acordado para este proyecto:

- Python
- Flask
- HTML
- Jinja
- SQLite
- JSON
- Programación orientada a objetos

No se usan frameworks adicionales ni librerías externas más allá de Flask y la base de datos SQLite.

## 5. Estructura de carpetas

La estructura del proyecto es la siguiente:

```text
proyecto_inventario/
├── app.py
├── database.py
├── models.py
├── services.py
├── requirements.txt
├── inventario.db
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── productos.html
│   ├── inventario.html
│   └── movimientos.html
├── static/
│   └── styles.css
└── README.md
```

### Descripción de cada archivo

- app.py: archivo principal de la aplicación Flask. Aquí se configuran las rutas y se inicia el servidor.
- database.py: contiene la conexión a SQLite y la creación de las tablas.
- models.py: define las clases principales del sistema con enfoque orientado a objetos.
- services.py: contiene la lógica de negocio para productos, variantes y movimientos.
- requirements.txt: lista las dependencias necesarias para ejecutar la aplicación.
- inventario.db: base de datos SQLite del proyecto.
- templates/: contiene las plantillas HTML de la interfaz web con Jinja.
- static/: contiene los archivos CSS para el estilo visual.
- README.md: documentación del proyecto.

## 6. Base de datos SQLite

La base de datos se llama inventario.db y tiene tres tablas principales:

### 6.1 Tabla productos

| Columna | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Clave primaria autoincremental |
| nombre | TEXT | Nombre del producto |
| categoria | TEXT | Categoría del producto |
| descripcion | TEXT | Descripción del producto |
| precio | REAL | Precio del producto |
| fecha_creacion | TEXT | Fecha de registro |

### 6.2 Tabla variantes

| Columna | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Clave primaria autoincremental |
| producto_id | INTEGER | Clave foránea hacia productos.id |
| talla | TEXT | Talla de la variante |
| color | TEXT | Color de la variante |
| stock_actual | INTEGER | Cantidad disponible actualmente |
| stock_minimo | INTEGER | Cantidad mínima antes de alertar |

### 6.3 Tabla movimientos

| Columna | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Clave primaria autoincremental |
| variante_id | INTEGER | Clave foránea hacia variantes.id |
| tipo | TEXT | Tipo de movimiento: entrada, salida o inicial |
| cantidad | INTEGER | Cantidad asociada al movimiento |
| fecha | TEXT | Fecha del movimiento |
| detalle | TEXT | Motivo o descripción del movimiento |

### 6.4 Relaciones

La relación entre las tablas es la siguiente:

- Un producto puede tener muchas variantes.
- Una variante puede tener muchos movimientos.

Esto se representa así:

- productos.id -> variantes.producto_id
- variantes.id -> movimientos.variante_id

Estas relaciones permiten mantener el inventario organizado y hacer seguimiento del historial de cada variante.

## 7. Flujo de funcionamiento

La aplicación sigue este flujo básico:

1. La administradora registra un producto.
2. Luego registra variantes del producto, con talla, color y cantidad inicial.
3. La app guarda esos datos en SQLite.
4. La administradora puede registrar movimientos de entrada o salida.
5. El sistema actualiza el stock actual de la variante.
6. Si el stock llega al mínimo configurado, aparece una alerta.
7. El historial de movimientos queda guardado para consulta posterior.
8. La app también ofrece una vista de inventario y una ruta JSON con los productos.

## 8. Requisitos de instalación

Necesitas tener Python 3 instalado en el sistema.

## 9. Instalación y ejecución

Desde la terminal, ejecuta los siguientes comandos:

```bash
cd /Users/evelynchirino/Documents/proyecto_inventario
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Una vez ejecutado, la aplicación quedará disponible en:

```text
http://127.0.0.1:5001
```

Se recomienda abrir la URL en Safari para probar la interfaz.

## 10. Cómo probar las funciones principales

### 10.1 Registrar un producto

1. Entra a la ruta:

```text
http://127.0.0.1:5001/productos
```

2. Completa el formulario con:
   - nombre
   - categoría
   - descripción
   - precio

3. Guarda el producto.

### 10.2 Registrar una variante

En la misma vista de productos:

1. Selecciona el producto creado
2. Ingresa la talla
3. Ingresa el color
4. Define la cantidad inicial
5. Define el stock mínimo
6. Guarda la variante

### 10.3 Consultar inventario

Ve a la ruta:

```text
http://127.0.0.1:5001/inventario
```

Aquí podrás ver:

- nombre del producto
- categoría
- talla
- color
- stock actual
- stock mínimo
- alertas de stock bajo

### 10.4 Registrar movimientos

Ve a la ruta:

```text
http://127.0.0.1:5001/movimientos
```

Allí puedes hacer lo siguiente:

- registrar una entrada
- registrar una salida
- escribir un motivo o detalle
- ver cómo cambia el stock actual

### 10.5 Probar validación de salidas

Para comprobar la validación:

1. selecciona una variante con stock disponible
2. intenta registrar una salida con una cantidad mayor a la disponible
3. la aplicación rechazará el movimiento y mostrará un mensaje de error

Esto evita que el sistema permita retirar más unidades de las existentes.

### 10.6 Probar la ruta JSON

Abre la siguiente URL en el navegador:

```text
http://127.0.0.1:5001/api/productos
```

Se mostrará una respuesta JSON con la información de los productos registrados y sus variantes.

## 11. Consideraciones importantes

- La aplicación guarda la información en SQLite en el archivo inventario.db.
- No se borran ni reinician los datos al ejecutar la app.
- La base de datos se crea automáticamente si no existe.
- La aplicación está configurada para ejecutarse en la dirección 127.0.0.1 y el puerto 5001.
- La versión actual incluye los elementos funcionales implementados hasta este punto.

## 12. Conclusión

Este proyecto permite llevar un control básico pero útil del inventario de una tienda de ropa, calzado y accesorios. A través de una interfaz sencilla y una base de datos local, se puede registrar productos, gestionar variantes, consultar existencias, registrar movimientos y detectar stock bajo.

Es una primera versión funcional, clara y apropiada para presentar un proyecto académico, con una estructura simple y fácil de explicar.
