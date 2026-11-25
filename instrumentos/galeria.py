from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_safe

from .models import Instrumento
from .presentacion import COLORES_MARCA


CATEGORIAS = {
    "guitarras": "Guitarras",
    "bajos": "Bajos",
    "teclados": "Teclados",
    "baterias": "Percusion",
}


@require_safe
def categorias(request):
    nombres = dict(Instrumento.CATEGORIAS)
    salas = [(ruta, nombres[clave]) for ruta, clave in CATEGORIAS.items()]
    return render(request, "instrumentos/galeria_categorias.html", {"salas": salas})


@require_safe
def exhibicion(request, categoria):
    clave = CATEGORIAS.get(categoria)
    if clave is None:
        raise Http404("Categoría de exhibición inexistente.")

    instrumentos = Instrumento.objects.filter(categoria=clave).order_by("nombre", "pk")
    return render(request, "instrumentos/galeria_exhibicion.html", {
        "titulo": dict(Instrumento.CATEGORIAS)[clave],
        "instrumentos": instrumentos,
        "categoria": categoria,
        "acabados": [
            {"instrumento": instrumento, "color": COLORES_MARCA.get(instrumento.get_marca_display(), "")}
            for instrumento in instrumentos
        ],
    })
