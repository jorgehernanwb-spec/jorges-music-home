# Reglas de campos

Alta y edición comparten `InstrumentoForm`. El servidor valida todas las solicitudes POST. El navegador ofrece ayuda inmediata, controles nativos y formato sin dependencias.

El buscador del inventario admite hasta 20 caracteres. Si una URL GET supera ese límite, Django muestra el error sin ejecutar la búsqueda y conserva las selecciones de categoría y disponibilidad.

| Campo | Formulario y modelo | MariaDB |
| --- | --- | --- |
| Nombre | Obligatorio. El navegador limita la entrada a 20 caracteres. Django recorta los espacios exteriores y reduce los internos consecutivos antes de comprobar de 2 a 20 caracteres. El modelo exige al menos una letra y solo permite letras, espacios y guiones. | `VARCHAR(20)` tras aplicar 0003, `NOT NULL` y mínimo de 2 caracteres. |
| Marca | Selector obligatorio con Fender, Gibson, Yamaha, Roland e Ibanez, disponibles para cualquier categoría. | `VARCHAR(20)` y `NOT NULL`. La pertenencia a la lista se valida en Django. |
| Categoría | Selector obligatorio con Guitarras, Bajos, Teclados y Baterías. Baterías conserva la clave interna `Percusion`. | `VARCHAR(20)` y `NOT NULL`. La pertenencia a la lista se valida en Django. |
| Precio | Obligatorio. Entre 1 y 999.999. Admite hasta seis dígitos, con `$` opcional y un punto de miles cuando corresponde. `analizar_precio` devuelve un entero. `formatear_clp` lo presenta como `$100.000`. | Entero sin signo con `CHECK` de rango. La migración 0004 fija el nuevo máximo de 999.999. |
| Stock | Obligatorio. Control de texto con teclado numérico y máximo de tres dígitos. JavaScript bloquea caracteres no numéricos y rechaza pegados inválidos completos. Django acepta de 0 a 999. La interfaz muestra «Sin stock» (0), «Stock bajo» (1–2) o «Disponible» (3 o más). | Entero sin signo con `CHECK` de rango. El estado se calcula en la interfaz. |
| Descripción | Opcional. Hasta 100 caracteres. El contador y el límite nativo se aplican al escribir y pegar. | Columna `LONGTEXT` y `NOT NULL`. Una descripción vacía se almacena como cadena vacía. La migración 0003 fija el máximo en 100 caracteres. |

Con JavaScript activo, los controles numéricos bloquean inserciones inválidas mediante `beforeinput`, `paste` y `drop`, con respaldo en `input`. Un pegado con precio mal agrupado se rechaza completo y conserva el valor anterior. El texto `1.000` representa mil pesos. Django aplica los mismos límites al recibir el POST sin JavaScript.

La migración 0004 agrega el nuevo `CHECK` de precio antes de retirar el anterior. Revisa que los datos existentes cumplan el nuevo rango antes de aplicarla.

La migración 0005 actualiza los `choices` en el estado de Django. En MariaDB no genera SQL ni reescribe registros.

La [paleta de acabados](../../instrumentos/presentacion.py) se obtiene de la marca y se aplica a la muestra de edición. Cambiar la marca actualiza el acabado sin cambiar el precio.

`save()`, `create()` y `QuerySet.update()` no ejecutan automáticamente `full_clean()`. Usa el formulario para entradas web y llama a `full_clean()` cuando escribas instancias por otra vía y necesites sus validaciones. Las restricciones SQL se aplican también a las escrituras directas, con independencia de Django.

## Datos anteriores a JMH-002

En el entorno auditado, el instrumento existente tiene la marca `fender`. La edición preselecciona `Fender` por coincidencia sin distinguir mayúsculas. Solo un guardado válido cambia la grafía. Si aparece una marca histórica sin equivalencia, el operador debe elegir una marca válida al editar. El POST solo acepta los valores canónicos.

La migración 0002 agrega restricciones de longitud y actualiza el estado de los campos de Django. No reescribe marcas ni normaliza registros existentes. Antes de aplicarla en una base real, revisa las longitudes que exige y las marcas que necesitan revisión.

La migración 0003 ensancha la columna de nombre e instala el límite de 100 para la descripción antes de retirar la restricción anterior. Coordina su aplicación con el uso del nuevo formulario en el esquema real, ya que la columna debe admitir el nuevo máximo. El atributo HTML `maxlength` y el contador de descripción usan unidades UTF-16. Django y MariaDB cuentan caracteres Unicode, por lo que los caracteres fuera del plano básico pueden consumir dos unidades en el navegador.
