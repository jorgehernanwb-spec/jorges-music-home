
from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = "instrumentos"

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="instrumentos/fachada.html"),
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
