# Diagrama de flujo CRUD

**Objetivo.** Mostrar las decisiones del servidor para solicitudes GET y POST, incluido el tratamiento de entradas inválidas y del borrado protegido.

```mermaid
flowchart TD
    solicitud["Solicitud a una ruta del inventario"] --> metodo{"¿GET o POST?"}
    metodo -->|GET| lectura{"¿Qué ruta se abrió?"}
    lectura -->|Catálogo| listado["Consultar con ORM y renderizar catálogo"]
    lectura -->|Alta| nuevo["Renderizar formulario vacío"]
    lectura -->|Detalle, edición o eliminación| buscarGet{"¿Existe el instrumento?"}
    buscarGet -->|No| perdido["Responder 404"]
    buscarGet -->|Sí| pantalla["Renderizar ficha, edición precargada o confirmación"]
    metodo -->|POST de escritura| csrf{"¿Supera la comprobación CSRF?"}
    csrf -->|No| rechazo["Responder 403"]
    csrf -->|Sí| accion{"¿Qué operación solicitó?"}
    accion -->|Alta| datos["Vincular request.POST a InstrumentoForm"]
    accion -->|Edición o eliminación| buscarPost{"¿Existe el instrumento?"}
    buscarPost -->|No| perdido
    buscarPost -->|Sí, edición| datos
    buscarPost -->|Sí, eliminación confirmada| borrar["Ejecutar instrumento.delete() por ORM"]
    datos --> validacion{"¿is_valid() devuelve True?"}
    validacion -->|No| errores["Renderizar el formulario vinculado con errores"]
    validacion -->|Sí| guardar["Ejecutar formulario.save() por ORM"]
    guardar --> mensaje["Registrar mensaje de confirmación"]
    borrar --> mensaje
    mensaje --> redirigir["Redirigir al catálogo"]
```

El diagrama se centra en los métodos usados por la interfaz. En edición, el formulario recibe la instancia encontrada. En eliminación, el GET solo presenta la confirmación. Cancelar vuelve al catálogo sin enviar el POST. El middleware comprueba CSRF antes del POST de escritura y `is_valid()` se usa únicamente en alta y edición.

## Referencias

- [Vistas CRUD](../../instrumentos/views.py) · [Middleware en settings.py](../../tienda_musica/settings.py) · [Confirmación de eliminación](../../instrumentos/templates/instrumentos/confirmar_eliminar.html) · [Pruebas HTTP](../../instrumentos/tests.py)
