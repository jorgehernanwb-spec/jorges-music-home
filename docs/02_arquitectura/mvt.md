# Arquitectura MVT de JORGE’S MUSIC HOME

**Objetivo.** Explicar cómo una solicitud HTTP llega al inventario, cómo Django valida y guarda los datos, y cómo se construye la respuesta.

## Componentes

| Componente | Responsabilidad en el proyecto |
| --- | --- |
| Modelo | `Instrumento` define los campos persistentes, las opciones de marca y categoría, los validadores y las restricciones. El ORM traduce operaciones sobre instancias y consultas a SQL. |
| Vista | Las funciones de `views.py` coordinan la solicitud, la consulta por identificador, el formulario, los mensajes y la respuesta. |
| Plantilla | Los archivos HTML heredan de `base.html` y presentan el catálogo, la ficha, los formularios y la confirmación de borrado. Alta y edición incluyen el mismo fragmento de campos. |
| Formulario | `InstrumentoForm` es el `ModelForm` compartido por alta y edición. Convierte los datos recibidos, valida campos y vincula el resultado al modelo. |
| URLs | La configuración del proyecto incluye las rutas de la aplicación. Cada ruta CRUD tiene un nombre dentro del espacio `instrumentos`. |

## Rutas y procesamiento HTTP

| Ruta | Nombre | Comportamiento |
| --- | --- | --- |
| `/` | `inicio` | Redirige temporalmente al catálogo. |
| `/instrumentos/` | `lista` | El GET muestra los instrumentos ordenados por nombre. |
| `/instrumentos/nuevo/` | `crear` | El GET muestra el formulario vacío. El POST intenta crear el instrumento. |
| `/instrumentos/<int:pk>/` | `detalle` | El GET muestra la ficha. Un identificador inexistente devuelve 404. |
| `/instrumentos/<int:pk>/editar/` | `editar` | El GET carga la instancia. El POST intenta actualizarla. Un identificador inexistente devuelve 404. |
| `/instrumentos/<int:pk>/eliminar/` | `eliminar` | El GET muestra la confirmación. El POST ejecuta el borrado. Un identificador inexistente devuelve 404. |

En lectura, `Instrumento.objects.all().order_by("nombre")` prepara la consulta del catálogo y `get_object_or_404(Instrumento, pk=pk)` obtiene la fila de la ficha, edición o borrado. La vista pasa los resultados a la plantilla con `render()`.

En alta, la vista construye `InstrumentoForm(request.POST)`. En edición, usa `InstrumentoForm(request.POST, instance=instrumento)`, de modo que `save()` actualice la fila seleccionada. Ambas ramas llaman a `is_valid()` antes de guardar. Un formulario inválido vuelve a la misma pantalla con sus errores. Si el guardado tiene éxito, Django registra un mensaje con `messages.success()` y redirige a `instrumentos:lista`.

El middleware CSRF valida las solicitudes POST y los formularios de escritura incluyen `{% csrf_token %}`. Al confirmar el borrado, la vista invoca `instrumento.delete()`, registra el mensaje y redirige al catálogo. La pantalla de confirmación se abre con GET y no escribe en la base.

## MariaDB y validación por capas

`settings.py` configura el backend `django.db.backends.mysql` para MariaDB mediante mysqlclient. El nombre de la base, el usuario y los demás parámetros se leen del entorno. Las credenciales locales se mantienen fuera de los documentos. Las migraciones crean y ajustan la tabla `instrumentos_instrumento`.

| Capa | Controles |
| --- | --- |
| Navegador | HTML aporta selectores, campos obligatorios y límites de entrada. `validaciones.js` ayuda con la escritura numérica, el formato CLP y el contador de descripción. |
| Django | El formulario y el modelo comprueban nombre de 2 a 20 caracteres, 13 marcas, seis categorías, precio de $1 a $999.999 CLP, stock de 0 a 999 y descripción opcional de hasta 100 caracteres. El servidor valida las solicitudes aunque JavaScript esté desactivado. |
| MariaDB | La longitud declarada de la columna y los `CHECK` protegen el nombre de 2 a 20 caracteres, la descripción de hasta 100 y los rangos de precio y stock. Las listas de marca y categoría y los caracteres del nombre se comprueban en Django. |

Por ejemplo, `PrecioCLPField.to_python()` usa `analizar_precio()` para convertir `$100.000` al entero `100000`. El ORM guarda ese entero y el filtro de plantilla `clp` vuelve a mostrar el importe con formato chileno. Las escrituras directas mediante ORM requieren validación explícita si deben aplicar todas las reglas de Django.

## Referencias

- [Rutas del proyecto](../../tienda_musica/urls.py) · [Rutas de instrumentos](../../instrumentos/urls.py) · [Vistas](../../instrumentos/views.py)
- [Modelo](../../instrumentos/models.py) · [Formulario](../../instrumentos/forms.py) · [Validadores](../../instrumentos/validaciones.py) · [Filtro CLP](../../instrumentos/templatetags/instrumentos_formato.py)
- [Configuración](../../tienda_musica/settings.py) · [Migraciones](../../instrumentos/migrations/) · [Plantillas](../../instrumentos/templates/instrumentos/) · [JavaScript](../../instrumentos/static/instrumentos/js/validaciones.js)
- [Diagrama MVT](../03_diagramas/arquitectura_mvt.md) · [Reglas de campos](../06_validaciones/reglas_campos.md)
