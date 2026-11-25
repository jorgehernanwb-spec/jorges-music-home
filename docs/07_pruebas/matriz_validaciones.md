# Matriz de validaciones

Ejecuta `python manage.py check` y `python manage.py test` con el entorno virtual activo. Verifica que Django use un esquema de pruebas distinto de `tienda_musica` antes de ejecutar la suite.

| Campo | Aceptación | Rechazo | Evidencia |
| --- | --- | --- | --- |
| Nombre | Dos y veinte caracteres, tildes, ñ, guiones y espacios normalizados | Vacío, un carácter, veintiuno, números, símbolos, espacios, solo guiones y tabulaciones | POST de alta y edición, con comprobación del valor persistido y del límite HTML |
| Marca | Cinco marcas disponibles para todas las categorías y marca actual seleccionada en edición | Sin selección, marca retirada, marca ajena y grafía no canónica en POST | Ambos POST, edición de marca histórica sin escritura en GET y cambio de acabado sin alterar el precio |
| Categoría | Guitarras, Bajos, Teclados y Baterías (`Percusion`) | Sin selección, categoría retirada y opción ajena | Ambos POST, filtro de inventario y formulario precargado |
| Precio | 1, 1000, 100000, 999999 y agrupación CLP válida | Vacío, 0, 1000000, séptimo dígito, negativos, decimales, letras y agrupación inválida | Analizador, ambos POST, SQL directo, edición precargada, catálogo y detalle |
| Stock | 0, 1 y 999 | Vacío, 1000, cuatro dígitos, negativos, decimales y letras | Ambos POST, restricción SQL, `maxlength` y eventos de escritura y pegado |
| Descripción | Vacía y 100 caracteres con puntuación | 101 caracteres, incluso si son espacios | Ambos POST, restricción SQL, `maxlength` y contador |
| Buscador del inventario | Hasta 20 caracteres y filtros combinados | 21 caracteres o más enviados por GET | Límite HTML y rechazo en Django sin consultar el inventario. Se conservan los selectores. |

Ejecuta `node --test instrumentos/tests_js/validaciones.test.js` para comprobar escritura, pegado, arrastre, respaldo ante cambios inválidos, borrado y contador. Las pruebas JavaScript usan un DOM simulado. Las pruebas de Django verifican los atributos que inicializan ambos formularios.

Para la comprobación manual en Edge, recarga alta y edición con `Ctrl+F5`. En precio, escribe `100000` y verifica que aparezca `$100.000`. Intenta añadir una letra y un séptimo dígito. Selecciona el importe y pega `1.50` o `1000000`. El valor previo debe permanecer y el aviso debe mostrarse. Pega `$999.999` y comprueba que se acepta. En stock, escribe `999` e intenta añadir una letra y un cuarto dígito. Selecciona el valor y pega `1000` o `12a`, que deben rechazarse completos. Prueba borrar, seleccionar y reemplazar por un valor válido en ambos campos.

Las ocho pruebas de JMH-001 siguen cubriendo creación, consulta, 404, edición precargada, edición válida e inválida, confirmación sin borrado por GET y borrado por POST con CSRF. Las pruebas adicionales verifican que las entradas inválidas de alta o edición no cambien la fila existente ni creen filas nuevas, y que MariaDB rechace escrituras directas fuera de los límites de nombre, descripción, precio y stock.

## Pruebas de la galería

| Requisito | Evidencia automatizada |
| --- | --- |
| Acceso y cuatro vitrinas | Django comprueba los accesos de recepción, destinos, nombres, PNG disponibles y textos de acción. |
| Consulta sin cambios | Django compara los registros antes y después y verifica las claves internas, las salas vacías y el 404. |
| Visor y alternativa | Node comprueba geometría con volumen, normales y materiales, además del estado sin WebGL. Django comprueba el aviso y la tabla de marcas. |
| Carrusel circular y transición | Node comprueba cinco registros, retorno circular, desplazamiento y movimiento reducido. |
| Especificaciones y estados límite | Django comprueba datos reales, acabados, precio CLP y salas con cero o un registro. Node comprueba la sincronización con la selección, el cierre por clic exterior y el retorno de foco. |
| Cuatro salas y cambios del CRUD | Django comprueba las cuatro categorías y que agregar un quinto registro, editar su marca y eliminarlo se refleje en su sala. Node comprueba que las cuatro mallas tengan volumen y materiales con y sin acabado de marca. |

La revisión de distribución en escritorio y móvil, de foco visible y de rotación renderizada se realiza siguiendo el [caso de uso de la galería](../04_casos_de_uso/galeria.md).
