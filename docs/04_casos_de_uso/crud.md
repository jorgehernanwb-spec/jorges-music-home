# Casos de uso del inventario

**Objetivo.** Describir cómo el operador realiza las cuatro operaciones CRUD, qué valida el sistema y qué respuesta puede observar.

El **operador del inventario** utiliza el navegador con Django y MariaDB disponibles y con el esquema migrado. Las rutas del inventario actual no requieren autenticación. Las operaciones de escritura se envían por POST con CSRF.

La galería ofrece otro acceso de lectura a la ficha mediante el enlace de detalle. Desde allí se conservan las acciones y rutas de edición y confirmación de eliminación. El alta continúa disponible desde el inventario y la recepción. [Exploración de categorías](galeria.md)

Cada sala consulta MariaDB al abrirse. Los cambios de marca, nombre, categoría, descripción, precio y stock aparecen al volver a consultar. Los registros eliminados dejan de aparecer. **Ver en 3D**, desde el listado o el detalle, abre el registro por su ID y sigue funcionando si cambia de categoría. Los agotados conservan la acción.

## CREATE · Registrar un instrumento

- **Objetivo.** Incorporar un instrumento al catálogo.
- **Actor.** Operador del inventario.
- **Precondiciones.** El sistema está disponible y el operador puede abrir la pantalla de alta.
- **Flujo principal.** El operador abre **Nuevo instrumento**, completa los campos y envía el formulario. La vista valida `InstrumentoForm(request.POST)`, guarda y redirige al catálogo con el mensaje de registro correcto.
- **Flujos alternativos.** Si el formulario es inválido, se vuelve a mostrar con los errores y sin crear la fila. **Cancelar** vuelve al catálogo. El middleware responde con 403 a un POST que falla la comprobación CSRF.
- **Validaciones.** Se aplican las reglas de los seis campos y las restricciones de MariaDB indicadas más abajo.
- **Resultado esperado.** El instrumento aparece en el catálogo y puede consultarse en su ficha.

## READ · Consultar catálogo y ficha

- **Objetivo.** Revisar el inventario y los datos de un instrumento.
- **Actor.** Operador del inventario.
- **Precondiciones.** El sistema está disponible. Para mostrar una ficha, debe existir el instrumento identificado por la URL.
- **Flujo principal.** El operador abre el catálogo, que lista los instrumentos ordenados por nombre. Al seleccionar **Ver**, Django busca la fila por su clave primaria y muestra la ficha.
- **Flujos alternativos.** Si el catálogo está vacío, se muestra el aviso correspondiente. Si el identificador de una ficha no existe, Django responde con 404.
- **Validaciones.** La ruta de detalle utiliza un identificador entero y la vista comprueba su existencia con `get_object_or_404()`.
- **Resultado esperado.** Se muestra el contenido solicitado sin modificar registros.

La misma plantilla de detalle presenta las cuatro categorías. Muestra marca, categoría y precio CLP en tres tarjetas, una insignia con el stock disponible o **Sin stock**, y la descripción. El Inventario conserva su indicador de stock bajo. Desde la ficha se puede abrir el visor 3D, editar el instrumento o volver al catálogo.

## UPDATE · Editar un instrumento

- **Objetivo.** Cambiar los datos de un instrumento existente.
- **Actor.** Operador del inventario.
- **Precondiciones.** El instrumento existe y el operador puede abrir su pantalla de edición.
- **Flujo principal.** El sistema carga el formulario con la instancia. El operador cambia los campos y pulsa **Guardar cambios**. La vista valida el POST con la misma instancia, guarda y redirige al catálogo con el mensaje de actualización.
- **Flujos alternativos.** Los datos inválidos vuelven al formulario con errores y la fila permanece intacta. **Cancelar** vuelve a la ficha. Un identificador inexistente devuelve 404 y un POST que falla CSRF devuelve 403.
- **Validaciones.** Se aplican las mismas reglas que en CREATE. Si una marca histórica coincide sin distinguir mayúsculas, la vista del formulario presenta la opción canónica. La grafía persistida cambia únicamente al guardar una edición válida.
- **Resultado esperado.** La ficha y el catálogo reflejan los datos actualizados del mismo identificador.

## DELETE · Eliminar un instrumento

- **Objetivo.** Retirar un instrumento del inventario.
- **Actor.** Operador del inventario.
- **Precondiciones.** El instrumento existe y el operador puede abrir su confirmación.
- **Flujo principal.** El operador pulsa **Eliminar** y revisa el nombre en la pantalla de confirmación. Al pulsar **Confirmar eliminación**, el formulario envía un POST con token CSRF. La vista elimina la fila, muestra el mensaje y redirige al catálogo.
- **Flujos alternativos.** **Cancelar** vuelve al catálogo sin enviar el POST. Abrir la confirmación por GET conserva la fila. Un identificador inexistente devuelve 404 y un POST que falla CSRF devuelve 403.
- **Validaciones.** El middleware valida el token y la vista comprueba que el instrumento existe. El borrado se ejecuta únicamente en la rama POST.
- **Resultado esperado.** La fila ya no aparece en el catálogo y su detalle devuelve 404.

## Reglas de alta y edición

| Campo | Regla |
| --- | --- |
| Nombre | Obligatorio, de 2 a 20 caracteres después de normalizar espacios. Admite letras, incluidas tildes y ñ, espacios y guiones. Debe contener al menos una letra. |
| Marca | Obligatoria. Una de cinco opciones predefinidas. |
| Categoría | Obligatoria. Una de cuatro opciones predefinidas. |
| Precio | Obligatorio. Entero de $1 a $999.999 CLP y hasta seis dígitos. `$100.000` se almacena como el entero `100000`. |
| Stock | Obligatorio. Entero de 0 a 999 con hasta tres dígitos. |
| Descripción | Opcional, hasta 100 caracteres. |

## Referencias

- [Diagrama de casos de uso](../03_diagramas/casos_de_uso.md) · [Flujo CRUD](../03_diagramas/flujo_crud.md) · [Reglas de campos](../06_validaciones/reglas_campos.md)
- [Rutas](../../instrumentos/urls.py) · [Vistas](../../instrumentos/views.py) · [Formulario](../../instrumentos/forms.py) · [Pruebas](../../instrumentos/tests.py)
