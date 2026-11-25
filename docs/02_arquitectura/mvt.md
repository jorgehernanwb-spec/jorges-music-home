# Arquitectura MVT de JORGE’S MUSIC HOME

**Objetivo.** Explicar cómo una solicitud HTTP llega al inventario, cómo Django valida y guarda los datos, y cómo se construye la respuesta.

## Componentes

| Componente | Responsabilidad en el proyecto |
| --- | --- |
| Modelo | `Instrumento` define los campos persistentes, las opciones de marca y categoría, los validadores y las restricciones. El ORM traduce operaciones sobre instancias y consultas a SQL. |
| Vista | `views.py` coordina el CRUD. `galeria.py` sirve la portada de la colección y consulta los registros por categoría mediante el ORM. |
| Plantilla | El inventario hereda de `base.html` y comparte el fragmento de campos entre alta y edición. La colección usa `galeria_base.html` y plantillas separadas para vitrinas y salas. |
| Formulario | `InstrumentoForm` es el `ModelForm` compartido por alta y edición. Convierte los datos recibidos, valida campos y vincula el resultado al modelo. |
| URLs | La configuración del proyecto incluye las rutas de la aplicación. Cada ruta CRUD tiene un nombre dentro del espacio `instrumentos`. |

## Rutas y procesamiento HTTP

| Ruta | Nombre | Comportamiento |
| --- | --- | --- |
| `/` | `inicio` | `TemplateView` muestra la fachada. El enlace de las puertas lleva a `/recepcion/`. |
| `/recepcion/` | `recepcion` | Muestra la recepción y el menú principal. |
| `/coleccion/` | `coleccion` | Muestra las cuatro vitrinas con los nombres del modelo. |
| `/coleccion/<slug:categoria>/` | `coleccion_categoria` | GET y HEAD muestran la sala y sus registros actuales. Las cuatro salas comparten visor y carrusel. Un slug desconocido devuelve 404. |
| `/coleccion/instrumento/<int:pk>/` | `coleccion_instrumento` | Consulta la categoría vigente y redirige a su sala con `?instrumento=<id>`. Si el registro ya no existe, vuelve a las categorías. |
| `/mundo-musical/` | `mundo_musical` | Entrada de la sección educativa en preparación. |
| `/instrumentos/` | `lista` | El GET muestra los instrumentos ordenados por nombre. |
| `/instrumentos/nuevo/` | `crear` | El GET muestra el formulario vacío. El POST intenta crear el instrumento. |
| `/instrumentos/<int:pk>/` | `detalle` | El GET muestra la ficha. Un identificador inexistente devuelve 404. |
| `/instrumentos/<int:pk>/editar/` | `editar` | El GET carga la instancia. El POST intenta actualizarla. Un identificador inexistente devuelve 404. |
| `/instrumentos/<int:pk>/eliminar/` | `eliminar` | El GET muestra la confirmación. El POST ejecuta el borrado. Un identificador inexistente devuelve 404. |

En lectura, el inventario ordena por nombre y clave primaria y puede filtrar por búsqueda, categoría y stock. `get_object_or_404(Instrumento, pk=pk)` obtiene la fila de la ficha, edición o borrado. La vista de exhibición traduce el slug a una clave interna (por ejemplo, `baterias` a `Percusion`) y filtra por categoría. Django crea las fichas HTML y obtiene el acabado desde `presentacion.py`. El carrusel cambia de registro en el navegador. Three.js y GLTFLoader cargan un GLB estático por sala y reutilizan su escena para todos los registros. [Recursos 3D](recursos_3d.md)

Django traduce el identificador solicitado a la posición inicial del carrusel dentro de la consulta ordenada. La plantilla entrega esa posición junto con las fichas. Se representa una pieza por registro y el stock se presenta como dato de la ficha.

En alta, la vista construye `InstrumentoForm(request.POST)`. En edición, usa `InstrumentoForm(request.POST, instance=instrumento)`, de modo que `save()` actualice la fila seleccionada. Ambas ramas llaman a `is_valid()` antes de guardar. Un formulario inválido vuelve a la misma pantalla con sus errores. Si el guardado tiene éxito, Django registra un mensaje con `messages.success()` y redirige a `instrumentos:lista`.

El middleware CSRF valida las solicitudes POST y los formularios de escritura incluyen `{% csrf_token %}`. Al confirmar el borrado, la vista invoca `instrumento.delete()`, registra el mensaje y redirige al catálogo. La pantalla de confirmación se abre con GET y no escribe en la base.

## MariaDB y validación por capas

`settings.py` configura el backend `django.db.backends.mysql` para MariaDB mediante mysqlclient. El nombre de la base, el usuario y los demás parámetros se leen del entorno. Las credenciales locales se mantienen fuera de los documentos. Las migraciones crean y ajustan la tabla `instrumentos_instrumento`.

| Capa | Controles |
| --- | --- |
| Navegador | HTML aporta selectores, campos obligatorios y límites de entrada. `validaciones.js` ayuda con la escritura numérica, el formato CLP y el contador de descripción. |
| Django | El formulario y el modelo comprueban nombre de 2 a 20 caracteres, cinco marcas, cuatro categorías, precio de $1 a $999.999 CLP, stock de 0 a 999 y descripción opcional de hasta 100 caracteres. El servidor valida las solicitudes aunque JavaScript esté desactivado. |
| MariaDB | La longitud declarada de la columna y los `CHECK` protegen el nombre de 2 a 20 caracteres, la descripción de hasta 100 y los rangos de precio y stock. Las listas de marca y categoría y los caracteres del nombre se comprueban en Django. |

Por ejemplo, `PrecioCLPField.to_python()` usa `analizar_precio()` para convertir `$100.000` al entero `100000`. El ORM guarda ese entero y el filtro de plantilla `clp` vuelve a mostrar el importe con formato chileno. Las escrituras directas mediante ORM requieren validación explícita si deben aplicar todas las reglas de Django.

## Referencias

- [Rutas del proyecto](../../tienda_musica/urls.py) · [Rutas de instrumentos](../../instrumentos/urls.py) · [Vistas](../../instrumentos/views.py)
- [Modelo](../../instrumentos/models.py) · [Formulario](../../instrumentos/forms.py) · [Validadores](../../instrumentos/validaciones.py) · [Filtro CLP](../../instrumentos/templatetags/instrumentos_formato.py)
- [Configuración](../../tienda_musica/settings.py) · [Migraciones](../../instrumentos/migrations/) · [Plantillas](../../instrumentos/templates/instrumentos/) · [JavaScript](../../instrumentos/static/instrumentos/js/validaciones.js)
- [Diagrama MVT](../03_diagramas/arquitectura_mvt.md) · [Reglas de campos](../06_validaciones/reglas_campos.md)
- [Vistas de galería](../../instrumentos/galeria.py) · [Casos de uso de la galería](../04_casos_de_uso/galeria.md)
