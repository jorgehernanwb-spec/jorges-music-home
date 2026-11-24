# Matriz de validaciones

Ejecuta `python manage.py check` y `python manage.py test` con el entorno virtual activo. Verifica que Django use un esquema de pruebas distinto de `tienda_musica` antes de ejecutar la suite.

| Campo | Aceptación | Rechazo | Evidencia |
| --- | --- | --- | --- |
| Nombre | Dos y veinte caracteres, tildes, ñ, guiones y espacios normalizados | Vacío, un carácter, veintiuno, números, símbolos, espacios, solo guiones y tabulaciones | POST de alta y edición, con comprobación del valor persistido y del límite HTML |
| Marca | Las trece marcas y selección de la marca actual en edición | Sin selección, marca ajena y grafía no canónica en POST | Ambos POST, edición de marca histórica sin escritura en GET |
| Categoría | Las seis opciones y selección de la categoría actual en edición | Sin selección y opción ajena | Ambos POST y formulario precargado |
| Precio | 1, 1000, 100000, 999999 y agrupación CLP válida | Vacío, 0, 1000000, séptimo dígito, negativos, decimales, letras y agrupación inválida | Analizador, ambos POST, SQL directo, edición precargada, catálogo y detalle |
| Stock | 0, 1 y 999 | Vacío, 1000, cuatro dígitos, negativos, decimales y letras | Ambos POST, restricción SQL, `maxlength` y eventos de escritura y pegado |
| Descripción | Vacía y 100 caracteres con puntuación | 101 caracteres, incluso si son espacios | Ambos POST, restricción SQL, `maxlength` y contador |

Ejecuta `node --test instrumentos/tests_js/validaciones.test.js` para comprobar escritura, pegado, arrastre, respaldo ante cambios inválidos, borrado y contador. Las pruebas JavaScript usan un DOM simulado. Las pruebas de Django verifican los atributos que inicializan ambos formularios.

Para la comprobación manual en Edge, recarga alta y edición con `Ctrl+F5`. En precio, escribe `100000` y verifica que aparezca `$100.000`. Intenta añadir una letra y un séptimo dígito. Selecciona el importe y pega `1.50` o `1000000`. El valor previo debe permanecer y el aviso debe mostrarse. Pega `$999.999` y comprueba que se acepta. En stock, escribe `999` e intenta añadir una letra y un cuarto dígito. Selecciona el valor y pega `1000` o `12a`, que deben rechazarse completos. Prueba borrar, seleccionar y reemplazar por un valor válido en ambos campos.

Las ocho pruebas de JMH-001 siguen cubriendo creación, consulta, 404, edición precargada, edición válida e inválida, confirmación sin borrado por GET y borrado por POST con CSRF. Las pruebas adicionales verifican que las entradas inválidas de alta o edición no cambien la fila existente ni creen filas nuevas, y que MariaDB rechace escrituras directas fuera de los límites de nombre, descripción, precio y stock.
