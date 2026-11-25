from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_safe

from .contenido_musical import ARTICULOS


@require_safe
def portada(request):
    return render(request, "instrumentos/mundo_portada.html", {"articulos": ARTICULOS.values()})


@require_safe
def leer(request, slug):
    articulo = ARTICULOS.get(slug)
    if articulo is None:
        raise Http404("Artículo musical inexistente.")
    return render(request, "instrumentos/mundo_articulo.html", {"articulo": articulo})
