from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
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
def abrir_instrumento(request, pk):
    clave = Instrumento.objects.filter(pk=pk).values_list("categoria", flat=True).first()
    categoria = next((ruta for ruta, valor in CATEGORIAS.items() if valor == clave), None)
    if categoria is None:
        return redirect("instrumentos:coleccion")
    sala = reverse("instrumentos:coleccion_categoria", args=[categoria])
    return redirect(f"{sala}?instrumento={pk}")


@require_safe
def exhibicion(request, categoria):
    clave = CATEGORIAS.get(categoria)
    if clave is None:
        raise Http404("Categoría de exhibición inexistente.")

    instrumentos = Instrumento.objects.filter(categoria=clave).order_by("nombre", "pk")
    solicitado = request.GET.get("instrumento")
    indice = None
    if solicitado is not None:
        indice = next((i for i, pieza in enumerate(instrumentos) if str(pieza.pk) == solicitado), None)
    return render(request, "instrumentos/galeria_exhibicion.html", {
        "titulo": dict(Instrumento.CATEGORIAS)[clave],
        "instrumentos": instrumentos,
        "categoria": categoria,
        "indice_inicial": indice or 0,
        "seleccion_directa": indice is not None,
        "seleccion_invalida": solicitado is not None and indice is None,
        "acabados": [
            {"instrumento": instrumento, "color": COLORES_MARCA.get(instrumento.get_marca_display(), "")}
            for instrumento in instrumentos
        ],
    })
