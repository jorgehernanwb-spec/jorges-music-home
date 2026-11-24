# Diagrama de arquitectura MVT

**Objetivo.** Mostrar el recorrido entre navegador, Django y MariaDB, tanto al procesar datos como al presentar la respuesta.

```mermaid
flowchart LR
    subgraph cliente["Navegador"]
        navegador["Interfaz HTML y CSS"]
        js["validaciones.js"]
        js -->|Controla los campos| navegador
    end
    subgraph django["Aplicación Django"]
        rutas["URLs del proyecto y de instrumentos"]
        vistas["Funciones de views.py"]
        formulario["InstrumentoForm"]
        modelo["Modelo Instrumento"]
        orm["ORM de Django"]
        plantillas["Templates HTML"]
        rutas -->|Despacha| vistas
        vistas -->|Alta y edición| formulario
        vistas -->|Consulta y borrado| modelo
        formulario -->|Valida y guarda| modelo
        modelo --> orm
        vistas -->|Contexto para render| plantillas
    end
    base[("MariaDB")]
    navegador -->|Solicitud HTTP| rutas
    plantillas -->|HTML de respuesta| navegador
    vistas -->|Redirección HTTP| navegador
    orm <-->|SQL y resultados| base
```

Las rutas identifican la vista. La vista coordina el acceso a los datos y utiliza el formulario al escribir por alta o edición. Los templates producen HTML y el fragmento de campos carga el JavaScript que se ejecuta en el navegador. La conexión a MariaDB se configura en Django y el ORM genera las consultas.

## Referencias

- [Arquitectura MVT](../02_arquitectura/mvt.md) · [Rutas](../../instrumentos/urls.py) · [Vistas](../../instrumentos/views.py) · [Configuración](../../tienda_musica/settings.py)
- [Fragmento de campos](../../instrumentos/templates/instrumentos/_campos_formulario.html) · [JavaScript](../../instrumentos/static/instrumentos/js/validaciones.js)
