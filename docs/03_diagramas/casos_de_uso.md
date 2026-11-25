# Diagrama de casos de uso

**Objetivo.** Mostrar las acciones del operador en la galería y el inventario web.

```mermaid
flowchart LR
    actor["Persona que utiliza la tienda"]
    subgraph inventario["JORGE'S MUSIC HOME"]
        galeria(["Explorar categorías"])
        sala(["Consultar instrumentos de una categoría"])
        girar(["Girar el modelo 3D de la categoría"])
        alternar(["Recorrer instrumentos de la sala"])
        leerMundo(["Consultar Mundo musical"])
        leerHistoria(["Consultar Nuestra historia"])
        verEnTresD(["Abrir un registro del inventario en 3D"])
        especificaciones(["Ver especificaciones de la selección"])
        catalogo(["Consultar inventario"])
        detalle(["Consultar detalle"])
        registrar(["Registrar instrumento"])
        editar(["Editar instrumento"])
        eliminar(["Eliminar instrumento"])
        confirmar(["Confirmar eliminación"])
        eliminar -. requiere .-> confirmar
    end
    actor --- galeria
    actor --- sala
    actor --- girar
    actor --- alternar
    actor --- leerMundo
    actor --- leerHistoria
    actor --- verEnTresD
    actor --- especificaciones
    actor --- catalogo
    actor --- detalle
    actor --- registrar
    actor --- editar
    actor --- eliminar
```

La exploración abre cuatro salas de solo lectura. Cada una permite recorrer sus registros y girar su GLB cuando está disponible. El vínculo punteado indica que el borrado requiere confirmación. [Casos de uso del inventario](../04_casos_de_uso/crud.md) · [Casos de uso de la galería](../04_casos_de_uso/galeria.md)

## Referencias

- [Rutas](../../instrumentos/urls.py) · [Funciones CRUD](../../instrumentos/views.py) · [Confirmación de eliminación](../../instrumentos/templates/instrumentos/confirmar_eliminar.html)
