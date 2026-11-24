
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Instrumento
from .forms import InstrumentoForm


def listar_instrumentos(request):
    instrumentos = Instrumento.objects.all().order_by("nombre")

    return render(request, "instrumentos/lista.html", {
        "instrumentos": instrumentos
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
        "instrumento": instrumento
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
