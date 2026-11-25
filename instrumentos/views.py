
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from .models import Instrumento
from .forms import InstrumentoForm
from .presentacion import COLORES_MARCA


BUSQUEDA_MAX = 20


def listar_instrumentos(request):
    entrada_busqueda = request.GET.get("q", "")
    busqueda_invalida = len(entrada_busqueda) > BUSQUEDA_MAX
    busqueda = "" if busqueda_invalida else entrada_busqueda.strip()
    categoria = request.GET.get("categoria", "")
    disponibilidad = request.GET.get("disponibilidad", "")
    categorias = Instrumento.CATEGORIAS
    if categoria not in dict(categorias):
        categoria = ""
    if disponibilidad not in ("con", "sin"):
        disponibilidad = ""

    inventario = Instrumento.objects.all()
    instrumentos = inventario.none() if busqueda_invalida else inventario.order_by("nombre", "pk")
    if busqueda:
        instrumentos = instrumentos.filter(
            Q(nombre__icontains=busqueda) | Q(marca__icontains=busqueda)
        )
    if categoria:
        instrumentos = instrumentos.filter(categoria=categoria)
    if disponibilidad == "con":
        instrumentos = instrumentos.filter(stock__gt=0)
    elif disponibilidad == "sin":
        instrumentos = instrumentos.filter(stock=0)

    filtros_activos = bool(busqueda or categoria or disponibilidad)
    inventario_vacio = (
        not busqueda_invalida and not instrumentos
        and (not filtros_activos or not inventario.exists())
    )

    return render(request, "instrumentos/lista.html", {
        "instrumentos": instrumentos,
        "busqueda": busqueda,
        "busqueda_max": BUSQUEDA_MAX,
        "busqueda_invalida": busqueda_invalida,
        "categoria_seleccionada": categoria,
        "disponibilidad": disponibilidad,
        "categorias": categorias,
        "inventario_vacio": inventario_vacio,
    })


def detalle_instrumento(request, pk):
    instrumento = get_object_or_404(Instrumento, pk=pk)

    return render(request, "instrumentos/detalle.html", {
        "instrumento": instrumento
    })


def crear_instrumento(request):
    if request.method == "POST":
        formulario = InstrumentoForm(request.POST)

        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Instrumento registrado correctamente.")
            return redirect("instrumentos:lista")
    else:
        formulario = InstrumentoForm()

    return render(request, "instrumentos/crear.html", {
        "formulario": formulario
    })


def editar_instrumento(request, pk):
    instrumento = get_object_or_404(Instrumento, pk=pk)

    if request.method == "POST":
        formulario = InstrumentoForm(request.POST, instance=instrumento)

        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Instrumento actualizado correctamente.")
            return redirect("instrumentos:lista")
    else:
        formulario = InstrumentoForm(instance=instrumento)

    return render(request, "instrumentos/editar.html", {
        "formulario": formulario,
        "instrumento": instrumento,
        "colores_marca": COLORES_MARCA,
        "color_marca": COLORES_MARCA.get(formulario["marca"].value()),
    })


def eliminar_instrumento(request, pk):
    instrumento = get_object_or_404(Instrumento, pk=pk)

    if request.method == "POST":
        instrumento.delete()
        messages.success(request, "Instrumento eliminado correctamente.")
        return redirect("instrumentos:lista")

    return render(request, "instrumentos/confirmar_eliminar.html", {
        "instrumento": instrumento
    })
