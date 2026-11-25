
from django.urls import path
from django.views.generic import TemplateView
from . import views
from . import galeria

app_name = "instrumentos"

urlpatterns = [
    path(
        "",
        TemplateView.as_view(template_name="instrumentos/fachada.html"),
        name="inicio"
    ),
    path(
        "recepcion/",
        TemplateView.as_view(template_name="instrumentos/recepcion.html"),
        name="recepcion",
    ),
    path(
        "coleccion/",
        galeria.categorias,
        name="coleccion",
    ),
    path("coleccion/<slug:categoria>/", galeria.exhibicion, name="coleccion_categoria"),
    path("coleccion/instrumento/<int:pk>/", galeria.abrir_instrumento, name="coleccion_instrumento"),
    path(
        "mundo-musical/",
        TemplateView.as_view(
            template_name="instrumentos/seccion_recepcion.html",
            extra_context={
                "titulo": "Mundo musical",
                "descripcion": "Próximamente: historia de la música, instrumentos, géneros y curiosidades.",
            },
        ),
        name="mundo_musical",
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
