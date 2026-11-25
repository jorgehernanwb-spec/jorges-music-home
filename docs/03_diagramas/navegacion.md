# Mapa de navegación

**Objetivo.** Mostrar el recorrido web desde la fachada y los accesos que comparten la Recepción y el Inventario.

```mermaid
flowchart TD
    A["Fachada /"] -->|Puertas| B["Recepción /recepcion/"]
    B -->|Instrumentos| C["Colección /coleccion/"]
    C --> D["Sala 3D de la categoría"]
    B -->|Computador o menú| E["Inventario /instrumentos/"]
    B -->|Agregar instrumento| F["Crear"]
    E --> F
    E --> G["Consultar ficha"]
    E --> H["Editar"]
    E --> I["Confirmar eliminación"]
    E -->|Ver en 3D| J["Resolver instrumento por ID"]
    G -->|Ver en 3D| J
    J -->|Registro existente| D
    J -->|Registro inexistente| C
    B --> K["Mundo Musical /mundo-musical/"]
    K --> L["Artículo"]
    L -->|Volver| K
    B -->|Letrero o botón| M["Diálogo Nuestra historia"]
    M -->|Explorar instrumentos| C
    M -->|Mundo Musical| K
    M -->|Cerrar o Escape| B
```

El acceso por ID funciona también para instrumentos sin stock. Los formularios de alta y edición redirigen al inventario al guardar. La eliminación requiere confirmación y POST con CSRF. El cierre del diálogo devuelve el foco al acceso que lo abrió. [Rutas](../../instrumentos/urls.py) · [Arquitectura MVT](../02_arquitectura/mvt.md)
