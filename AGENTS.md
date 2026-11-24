# JORGE'S MUSIC HOME

Mantén la separación MVT de Django. El modelo define los datos y sus restricciones, el formulario valida las entradas, las vistas coordinan el flujo HTTP y las plantillas presentan los datos. Reutiliza el mismo formulario en alta y edición.

Para implementar un campo editable nuevo, define:

- Tipo de dato y si es obligatorio.
- Mínimo y máximo, cuando corresponda.
- Caracteres o valores permitidos.
- Validación del lado del servidor, aunque exista validación en el navegador.
- Mensajes de error claros en español.
- Pruebas de valores válidos, inválidos y casos límite.

Prueba los cambios de persistencia en una base aislada. Antes de aplicar una migración, inspecciona los datos existentes y el efecto del cambio. Mantén en el historial las migraciones ya publicadas.

Los límites de entrada del inventario son 20 caracteres para el nombre, 6 dígitos para el precio (de $1 a $999.999 CLP), 3 dígitos para el stock y 100 caracteres para la descripción. Conserva `maxlength` en los campos de texto sin formato y prueba que alta y edición rendericen los mismos límites. Rechaza las inserciones numéricas inválidas completas y conserva el último valor válido. No conviertas un importe inválido en uno distinto mediante recortes.

- [Reglas de campos](docs/06_validaciones/reglas_campos.md)
- [Matriz de validaciones](docs/07_pruebas/matriz_validaciones.md)
