# Diagrama de casos de uso

**Objetivo.** Mostrar las acciones del operador dentro del inventario web y dónde termina el alcance del sistema.

```mermaid
flowchart LR
    actor["Operador del inventario"]
    subgraph inventario["JORGE'S MUSIC HOME · Inventario web"]
        catalogo(["Consultar catálogo"])
        detalle(["Consultar detalle"])
        registrar(["Registrar instrumento"])
        editar(["Editar instrumento"])
        eliminar(["Eliminar instrumento"])
        confirmar(["Confirmar eliminación"])
        eliminar -. requiere .-> confirmar
    end
    actor --- catalogo
    actor --- detalle
    actor --- registrar
    actor --- editar
    actor --- eliminar
```

El operador representa a la persona que utiliza la interfaz local. El CRUD actual está disponible sin iniciar sesión. El recuadro agrupa las acciones del inventario y el vínculo punteado indica que el borrado requiere confirmar el envío. Los métodos y casos alternativos están en el [documento de casos de uso](../04_casos_de_uso/crud.md).

## Referencias

- [Rutas](../../instrumentos/urls.py) · [Funciones CRUD](../../instrumentos/views.py) · [Confirmación de eliminación](../../instrumentos/templates/instrumentos/confirmar_eliminar.html)
