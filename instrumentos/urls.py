
from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "instrumentos"

urlpatterns = [
    # Entrada temporal hasta crear la fachada vintage
    path(
        "",
        RedirectView.as_view(
            pattern_name="instrumentos:lista",
            permanent=False
        ),
        name="inicio"
    ),

    # READ - Consultar instrumentos
    path(
        "instrumentos/",
        views.listar_instrumentos,
        name="lista"
    ),

    # CREATE - Registrar instrumento
    path(
        "instrumentos/nuevo/",
        views.crear_instrumento,
        name="crear"
    ),

    # READ - Ver detalles
    path(
        "instrumentos/<int:pk>/",
        views.detalle_instrumento,
        name="detalle"
    ),

    # UPDATE - Editar instrumento
    path(
        "instrumentos/<int:pk>/editar/",
        views.editar_instrumento,
        name="editar"
    ),

    # DELETE - Eliminar instrumento
    path(
        "instrumentos/<int:pk>/eliminar/",
        views.eliminar_instrumento,
        name="eliminar"
    ),
]
