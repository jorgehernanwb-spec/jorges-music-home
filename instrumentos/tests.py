import re
from collections import Counter
from importlib import import_module

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.contrib.staticfiles import finders
from django.db import IntegrityError, connection, transaction
from django.db.migrations.executor import MigrationExecutor
from django.test import Client, SimpleTestCase, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import InstrumentoForm
from .models import Instrumento
from .validaciones import analizar_precio


class FachadaTests(SimpleTestCase):
    def test_inicio_muestra_solo_la_fachada_con_la_proporcion_original(self):
        response = self.client.get(reverse("instrumentos:inicio"))
        self.assertTemplateUsed(response, "instrumentos/fachada.html")
        self.assertTemplateNotUsed(response, "instrumentos/base.html")
        for etiqueta in ("<header", "<nav", "<form", "<button"):
            self.assertNotContains(response, etiqueta)
        self.assertContains(response, '<footer class="pie-global">', count=1)
        self.assertContains(response, 'width="1774" height="887"')
        self.assertContains(response, "instrumentos/img/fachada-principal.png")
        self.assertContains(response, "instrumentos/css/fachada.css")
        self.assertContains(response, "instrumentos/js/fachada.js")
        self.assertNotContains(response, "instrumentos/js/validaciones.js")

    def test_las_puertas_son_un_enlace_nativo_a_la_recepcion(self):
        response = self.client.get(reverse("instrumentos:inicio"))
        enlace = re.search(r'<a class="fachada-puertas"[^>]*>', response.content.decode())
        self.assertIsNotNone(enlace)
        self.assertIn(f'href="{reverse("instrumentos:recepcion")}"', enlace.group())
        self.assertIn('aria-label="Entrar a la tienda"', enlace.group())
        self.assertNotIn("tabindex", enlace.group())

    def test_el_formulario_conserva_navegacion_y_validaciones_propias(self):
        response = self.client.get(reverse("instrumentos:crear"))
        self.assertTemplateUsed(response, "instrumentos/base.html")
        self.assertContains(response, '<nav aria-label="Navegación principal">')
        self.assertContains(response, "instrumentos/js/validaciones.js")
        self.assertNotContains(response, "instrumentos/js/fachada.js")
        self.assertNotContains(response, "instrumentos/css/fachada.css")


class RecepcionTests(SimpleTestCase):
    def test_recepcion_usa_la_imagen_aprobada_y_tiene_menu_con_iconos(self):
        response = self.client.get(reverse("instrumentos:recepcion"))
        self.assertContains(response, "instrumentos/img/recepcion-principal.png")
        self.assertContains(response, 'width="1448" height="1086"')
        self.assertContains(response, 'aria-controls="menu-recepcion" aria-expanded="false"')
        self.assertContains(response, 'method="dialog"')
        self.assertContains(response, 'type="submit" autofocus')
        self.assertNotContains(response, 'aria-label="Accesos rápidos"')
        self.assertTemplateNotUsed(response, "instrumentos/base.html")
        for ruta, etiqueta in (
            ("recepcion", "Inicio"),
            ("coleccion", "Instrumentos"),
            ("lista", "Inventario"),
            ("crear", "Agregar instrumento"),
            ("mundo_musical", "Mundo musical"),
        ):
            actual = ' aria-current="page"' if ruta == "recepcion" else ""
            self.assertRegex(
                response.content.decode(),
                rf'(?s)<a href="{reverse(f"instrumentos:{ruta}")}"{actual}>\s*<svg[^>]*>.*?</svg>\s*{etiqueta}</a>',
            )

    def test_recepcion_tiene_zonas_interactivas_paneles_y_salida(self):
        response = self.client.get(reverse("instrumentos:recepcion"))
        self.assertContains(response, 'aria-label="Explorar instrumentos, guitarra ', count=6)
        self.assertContains(response, f'href="{reverse("instrumentos:coleccion")}"', count=8)
        self.assertContains(response, 'id="letrero-recepcion"')
        self.assertContains(response, 'aria-label="Abrir Nuestra historia desde el letrero Jorge\'s"')
        self.assertContains(response, 'aria-controls="menu-historia"', count=2)
        self.assertContains(response, 'id="menu-historia"', count=1)
        self.assertContains(response, 'aria-controls="menu-computador"', count=1)
        self.assertContains(response, 'id="menu-computador"', count=1)
        self.assertNotContains(response, 'aria-hidden="true">Administración')
        self.assertContains(response, "Nuestro compromiso")
        self.assertContains(response, f'class="recepcion-control recepcion-salida" href="{reverse("instrumentos:inicio")}"')
        escena = response.content.decode().split('<div class="recepcion-escena">', 1)[1].split("</div>", 1)[0]
        self.assertIn("recepcion-historia", escena)
        self.assertIn("recepcion-salida", escena)

    def test_mundo_musical_marca_la_opcion_activa(self):
        destino = reverse("instrumentos:mundo_musical")
        response = self.client.get(destino)
        self.assertContains(response, "<h1>Mundo musical</h1>", html=True)
        self.assertRegex(
            response.content.decode(),
            rf'(?s)<a href="{destino}" aria-current="page">\s*<svg[^>]*>.*?</svg>\s*Mundo musical</a>',
        )
        self.assertContains(
            response, f'<a class="recepcion-control" href="{reverse("instrumentos:recepcion")}">Inicio</a>',
            html=True,
        )


class GaleriaCategoriasTests(SimpleTestCase):
    def test_recepcion_y_las_cuatro_tarjetas_enlazan_sus_destinos(self):
        ruta = reverse("instrumentos:coleccion")
        self.assertContains(
            self.client.get(reverse("instrumentos:recepcion")), f'href="{ruta}"', count=8,
        )
        response = self.client.get(ruta)
        self.assertContains(response, "<h1>Nuestra colección</h1>", html=True)
        self.assertContains(response, 'class="galeria-sala"', count=4)
        self.assertContains(response, "Explorar colección", count=4)
        self.assertNotContains(response, "galeria-icono")
        for slug, nombre in (
            ("guitarras", "Guitarras"), ("bajos", "Bajos"),
            ("teclados", "Teclados"), ("baterias", "Baterías"),
        ):
            self.assertContains(response, f'href="{ruta}{slug}/"')
            self.assertContains(response, f'id="nombre-{slug}">{nombre}</span>')
            self.assertContains(response, f'aria-labelledby="accion-{slug} nombre-{slug}"')
            ruta_imagen = f"instrumentos/img/vitrina_{slug}.png"
            self.assertContains(response, ruta_imagen)
            self.assertIsNotNone(finders.find(ruta_imagen))

    def test_categoria_desconocida_y_escrituras_se_rechazan(self):
        self.assertEqual(self.client.get("/coleccion/percusion/").status_code, 404)
        self.assertEqual(self.client.post("/coleccion/guitarras/").status_code, 405)


class GaleriaExhibicionTests(TestCase):
    def test_categorias_consultan_los_registros_en_mariadb_sin_modificarlos(self):
        before = list(Instrumento.objects.order_by("pk").values())
        for slug, clave in (
            ("guitarras", "Guitarras"), ("bajos", "Bajos"),
            ("teclados", "Teclados"), ("baterias", "Percusion"),
        ):
            with self.subTest(slug=slug):
                response = self.client.get(f"/coleccion/{slug}/")
                esperado = Instrumento.objects.filter(categoria=clave).order_by("nombre", "pk")
                self.assertQuerySetEqual(response.context["instrumentos"], esperado)
                for instrumento in esperado:
                    detalle = reverse("instrumentos:detalle", args=[instrumento.pk])
                    self.assertContains(response, f'href="{detalle}"')
                self.assertContains(response, f'data-categoria="{slug}"')
                self.assertContains(response, "galeria-carrusel.mjs")
                self.assertContains(response, "Ver especificaciones")
                self.assertContains(response, 'class="pie-global"', count=1)
                self.assertContains(response, "data-acabado=", count=esperado.count())
        self.assertEqual(list(Instrumento.objects.order_by("pk").values()), before)

    def test_categoria_vacia_conserva_la_navegacion(self):
        Instrumento.objects.all().delete()
        for slug in ("guitarras", "bajos", "teclados", "baterias"):
            with self.subTest(slug=slug):
                response = self.client.get(f"/coleccion/{slug}/")
                self.assertContains(response, "Aún no hay instrumentos en esta categoría.")
                self.assertContains(response, 'href="/coleccion/"')
                self.assertNotContains(response, "data-carrusel")

    def test_guitarras_entrega_un_estado_alternativo_y_colores_centralizados(self):
        from .presentacion import COLORES_MARCA

        response = self.client.get("/coleccion/guitarras/")
        self.assertContains(response, 'data-visor-alternativo role="status"')
        self.assertContains(response, "Visor 3D no disponible.")
        self.assertContains(response, "galeria-carrusel.mjs")
        self.assertContains(response, "Ver especificaciones")
        self.assertContains(response, 'aria-haspopup="dialog"')
        self.assertContains(response, "<form method=\"dialog\">")
        self.assertNotContains(response, "guitarra-acabado")
        for pieza in response.context["acabados"]:
            instrumento = pieza["instrumento"]
            self.assertEqual(pieza["color"], COLORES_MARCA[instrumento.marca])
            self.assertContains(response, f'data-acabado="{pieza["color"]}"')
            self.assertContains(response, instrumento.descripcion)
            self.assertContains(response, f"{instrumento.stock} unidades")
        self.assertContains(response, "$189.990 CLP")

    def test_guitarras_con_cero_o_un_registro(self):
        guitarras = Instrumento.objects.filter(categoria="Guitarras")
        primera = guitarras.first()
        guitarras.exclude(pk=primera.pk).delete()
        response = self.client.get("/coleccion/guitarras/")
        self.assertContains(response, "data-acabado", count=1)
        self.assertContains(response, primera.descripcion)
        guitarras.delete()
        response = self.client.get("/coleccion/guitarras/")
        self.assertContains(response, "Aún no hay instrumentos en esta categoría.")
        self.assertNotContains(response, "data-carrusel")

    def test_sala_refleja_alta_edicion_y_eliminacion_del_inventario(self):
        from .presentacion import COLORES_MARCA

        datos = {
            "nombre": "Bajo de prueba", "marca": "Fender", "categoria": "Bajos",
            "precio": "123456", "stock": 8, "descripcion": "Modelo de prueba.",
        }
        ruta = "/coleccion/bajos/"
        self.assertRedirects(self.client.post(reverse("instrumentos:crear"), datos), reverse("instrumentos:lista"))
        bajo = Instrumento.objects.get(nombre=datos["nombre"])
        self.assertContains(self.client.get(ruta), "data-acabado=", count=5)
        detalle = reverse("instrumentos:detalle", args=[bajo.pk])
        datos["marca"] = "Ibanez"
        editar = reverse("instrumentos:editar", args=[bajo.pk])
        self.assertRedirects(self.client.post(editar, datos), reverse("instrumentos:lista"))
        response = self.client.get(ruta)
        pieza = next(pieza for pieza in response.context["acabados"] if pieza["instrumento"].pk == bajo.pk)
        self.assertEqual(pieza["color"], COLORES_MARCA["Ibanez"])
        self.assertEqual(pieza["instrumento"].precio, 123456)
        self.assertContains(response, "$123.456 CLP")
        eliminar = reverse("instrumentos:eliminar", args=[bajo.pk])
        self.assertRedirects(self.client.post(eliminar), reverse("instrumentos:lista"))
        response = self.client.get(ruta)
        self.assertContains(response, "data-acabado=", count=4)
        self.assertNotContains(response, f'href="{detalle}"')


class CatalogoInicialTests(TestCase):
    def repetir_migrate(self):
        call_command(
            "migrate", "instrumentos", "0006_cargar_catalogo_inicial",
            interactive=False, verbosity=0,
        )

    def test_instalacion_limpia_carga_catálogo_aprobado(self):
        instrumentos = list(Instrumento.objects.all())
        self.assertEqual(len(instrumentos), 16)
        self.assertEqual(Counter(i.categoria for i in instrumentos), {
            "Guitarras": 4, "Bajos": 4, "Teclados": 4, "Percusion": 4,
        })
        self.assertEqual({i.marca for i in instrumentos}, {"Fender", "Gibson", "Yamaha", "Roland", "Ibanez"})
        modelos = {
            "Pacifica", "RG GIO", "Stratocaster", "Les Paul", "TRBX", "SR300",
            "Jazz Bass", "Thunderbird", "PSR-E383", "GO:KEYS 5", "MX61",
            "JUNO-D6", "Rydeen", "TD-02K", "Stage Custom", "TD-07DMK",
        }
        self.assertEqual({i.descripcion.split(",", 1)[0].removeprefix("Modelo ") for i in instrumentos}, modelos)
        nombres = {
            "Guitarras": {"Guitarra eléctrica"},
            "Bajos": {"Bajo eléctrico"},
            "Teclados": {"Teclado digital"},
            "Percusion": {"Batería acústica", "Batería electrónica"},
        }
        for instrumento in instrumentos:
            with self.subTest(pk=instrumento.pk):
                self.assertIn(instrumento.nombre, nombres[instrumento.categoria])
                self.assertLessEqual(len(instrumento.descripcion), 100)
                instrumento.full_clean()

    def test_migrate_repetido_conserva_ediciones_y_no_recrea_borrados(self):
        instrumento = Instrumento.objects.get(descripcion__startswith="Modelo Pacifica,")
        editar = reverse("instrumentos:editar", args=[instrumento.pk])
        datos = {
            "nombre": "Guitarra de prueba", "marca": "Roland", "categoria": "Bajos",
            "precio": "$210.000", "stock": 0, "descripcion": "Descripción editada",
        }
        self.assertRedirects(self.client.post(editar, datos), reverse("instrumentos:lista"))

        eliminado = Instrumento.objects.get(descripcion__startswith="Modelo Rydeen,")
        eliminar = reverse("instrumentos:eliminar", args=[eliminado.pk])
        self.assertContains(self.client.get(eliminar), "Confirmar eliminación")
        self.assertRedirects(self.client.post(eliminar), reverse("instrumentos:lista"))

        antes = list(Instrumento.objects.order_by("pk").values_list())
        self.repetir_migrate()
        self.assertEqual(list(Instrumento.objects.order_by("pk").values_list()), antes)
        self.assertEqual(Instrumento.objects.count(), 15)
        self.assertFalse(Instrumento.objects.filter(pk=eliminado.pk).exists())
        instrumento.refresh_from_db()
        self.assertEqual(instrumento.precio, 210000)
        for campo in ("nombre", "marca", "categoria", "stock", "descripcion"):
            self.assertEqual(getattr(instrumento, campo), datos[campo])
        self.assertContains(self.client.get(editar), 'style="--acabado: #F1F0E9"')

    def test_carga_sobre_datos_existentes_conserva_una_coincidencia_y_otros_registros(self):
        Instrumento.objects.all().delete()
        manual = Instrumento.objects.create(
            nombre="Teclado digital", marca="Ibanez", categoria="Teclados",
            precio=100000, stock=0, descripcion="Ingreso manual.",
        )
        coincidencia = Instrumento.objects.create(
            nombre="Guitarra de sala", marca="Yamaha", categoria="Guitarras",
            precio=1, stock=1, descripcion="Modelo PACIFICA, unidad de demostración usada.",
        )
        antes = list(Instrumento.objects.order_by("pk").values_list())
        carga = import_module("instrumentos.migrations.0006_cargar_catalogo_inicial").cargar_catalogo
        estado = MigrationExecutor(connection).loader.project_state([("instrumentos", "0005_catalogo_categorias_marcas")])
        carga(estado.apps, connection.schema_editor())
        self.assertEqual(Instrumento.objects.count(), 17)
        self.assertEqual(
            list(Instrumento.objects.filter(pk__in=[manual.pk, coincidencia.pk]).order_by("pk").values_list()),
            antes,
        )
        self.assertEqual(Instrumento.objects.filter(descripcion__icontains="Pacifica").count(), 1)

    def test_inventario_filtra_las_baterias_roland_del_catalogo(self):
        respuesta = self.client.get(reverse("instrumentos:lista"), {
            "q": "Roland", "categoria": "Percusion", "disponibilidad": "con",
        })
        self.assertContains(respuesta, "Resultados: 2")
        self.assertContains(respuesta, "$499.990 CLP")
        self.assertContains(respuesta, "$899.990 CLP")
        self.assertNotContains(respuesta, "$399.990 CLP")


class InstrumentoCRUDTests(TestCase):
    datos = {
        "nombre": "Bajo Precision",
        "marca": "Fender",
        "categoria": "Bajos",
        "precio": 250000,
        "stock": 3,
        "descripcion": "Instrumento de cuatro cuerdas.",
    }

    @classmethod
    def setUpTestData(cls):
        Instrumento.objects.all().delete()
        cls.instrumento = Instrumento.objects.create(**cls.datos)

    def test_footer_global_unico_y_con_el_ano_actual(self):
        routes = [(name, ()) for name in ("inicio", "recepcion", "coleccion", "mundo_musical", "lista", "crear")]
        routes += [(name, (self.instrumento.pk,)) for name in ("detalle", "editar", "eliminar")]
        for name, args in routes:
            with self.subTest(ruta=name):
                response = self.client.get(reverse(f"instrumentos:{name}", args=args))
                self.assertContains(response, "<footer", count=1)
                self.assertContains(
                    response,
                    f"© {timezone.localdate().year} Jorge's Music Home · Todos los derechos reservados.",
                    count=1,
                )

    def test_el_alta_conserva_el_formulario_y_guarda(self):
        url = reverse("instrumentos:crear")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "instrumentos/crear.html")
        self.assertContains(response, '<h1 id="titulo-crear">Agregar instrumento</h1>', html=True)
        self.assertContains(response, "Incorpora un nuevo instrumento a nuestra colección")
        self.assertContains(response, f'<form method="post" action="{url}">')
        self.assertContains(response, "Guardar instrumento")
        self.assertContains(response, f'href="{reverse("instrumentos:lista")}" class="boton-secundario"')
        self.assertContains(response, 'name="nombre"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertTrue(all(campo.value() in (None, "") for campo in response.context["formulario"]))

        response = self.client.post(url, {**self.datos, "nombre": "Bajo Jazz"})
        self.assertRedirects(response, reverse("instrumentos:lista"))
        self.assertTrue(Instrumento.objects.filter(nombre="Bajo Jazz").exists())

    def test_detalle_muestra_la_ficha(self):
        response = self.client.get(
            reverse("instrumentos:detalle", args=[self.instrumento.pk])
        )
        self.assertTemplateUsed(response, "instrumentos/detalle.html")
        for contenido in (
            "Bajo Precision", "Fender", "Bajos", "$250.000 CLP",
            "3 unidades", self.datos["descripcion"], "Editar instrumento",
            "Volver al catálogo",
        ):
            self.assertContains(response, contenido)

    def test_id_inexistente_devuelve_404(self):
        for ruta in ("detalle", "editar", "eliminar"):
            with self.subTest(ruta=ruta):
                url = reverse(f"instrumentos:{ruta}", args=[self.instrumento.pk + 1])
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_edicion_carga_los_datos_actuales(self):
        url = reverse("instrumentos:editar", args=[self.instrumento.pk])
        response = self.client.get(url)
        self.assertTemplateUsed(response, "instrumentos/editar.html")
        self.assertContains(response, "Editar instrumento")
        self.assertContains(response, "<strong>Bajo Precision</strong>", html=True)
        self.assertContains(response, f'<form method="post" action="{url}">')
        self.assertContains(response, "Guardar cambios")
        self.assertContains(response, f'href="{reverse("instrumentos:detalle", args=[self.instrumento.pk])}">Cancelar')
        self.assertContains(response, 'value="Bajo Precision"')
        self.assertContains(response, 'value="$250.000"')
        self.assertContains(response, '<option value="Fender" selected>Fender</option>', html=True)
        self.assertContains(response, '<option value="Bajos" selected>Bajos</option>', html=True)
        formulario = response.context["formulario"]
        self.assertIsInstance(formulario, InstrumentoForm)
        self.assertFalse(formulario.is_bound)
        for campo, dato in self.datos.items():
            self.assertEqual(formulario.initial[campo], dato)
            if campo != "precio":
                self.assertEqual(formulario[campo].value(), dato)

    def test_edicion_valida_actualiza_y_confirma(self):
        url = reverse("instrumentos:editar", args=[self.instrumento.pk])
        datos = {**self.datos, "nombre": "Bajo Jazz", "precio": 300000, "stock": 7}
        response = self.client.post(url, datos, follow=True)
        self.assertRedirects(response, reverse("instrumentos:lista"))
        self.assertContains(response, "Instrumento actualizado correctamente.")
        self.instrumento.refresh_from_db()
        for campo, dato in datos.items():
            self.assertEqual(getattr(self.instrumento, campo), dato)
        self.assertEqual(Instrumento.objects.count(), 1)

    def test_edicion_invalida_muestra_errores_y_conserva_datos(self):
        url = reverse("instrumentos:editar", args=[self.instrumento.pk])
        response = self.client.post(url, {
            **self.datos, "nombre": "Bajo Jazz", "marca": "Yamaha",
            "categoria": "Guitarras", "stock": 1000,
        })
        self.assertTemplateUsed(response, "instrumentos/editar.html")
        self.assertIn("stock", response.context["formulario"].errors)
        self.assertContains(response, 'class="errorlist"')
        self.assertContains(response, 'id="id_stock_errores"')
        self.assertContains(response, 'aria-describedby="id_stock_errores"')
        self.assertContains(response, "<strong>Bajo Precision</strong>", html=True)
        self.assertContains(response, "<div><dt>Marca</dt><dd>Fender</dd></div>", html=True)
        self.assertContains(response, "<div><dt>Categoría</dt><dd>Bajos</dd></div>", html=True)
        self.assertContains(response, 'value="Bajo Jazz"')
        self.assertContains(response, '<option value="Yamaha" selected>Yamaha</option>', html=True)
        self.assertContains(response, '<option value="Guitarras" selected>Guitarras</option>', html=True)
        self.assertContains(response, 'value="1000"')
        self.instrumento.refresh_from_db()
        for campo, dato in self.datos.items():
            self.assertEqual(getattr(self.instrumento, campo), dato)

    def test_alta_y_edicion_muestran_errores_en_los_campos_obligatorios(self):
        rutas = (reverse("instrumentos:crear"), reverse("instrumentos:editar", args=[self.instrumento.pk]))
        for ruta in rutas:
            with self.subTest(ruta=ruta):
                response = self.client.post(ruta, {})
                campos = {"nombre", "marca", "categoria", "precio", "stock"}
                self.assertEqual(set(response.context["formulario"].errors), campos)
                for campo in campos:
                    self.assertContains(response, f'<label for="id_{campo}">')
                    self.assertContains(response, f'id="id_{campo}_errores"')
                self.assertContains(response, 'class="grupo-campo grupo-campo--ancho"')

    def test_get_muestra_confirmacion_y_no_elimina(self):
        url = reverse("instrumentos:eliminar", args=[self.instrumento.pk])
        response = self.client.get(url)
        self.assertTemplateUsed(response, "instrumentos/confirmar_eliminar.html")
        self.assertContains(response, self.instrumento.nombre)
        self.assertContains(response, "<div><dt>Marca</dt><dd>Fender</dd></div>", html=True)
        self.assertContains(response, "<div><dt>Categoría</dt><dd>Bajos</dd></div>", html=True)
        self.assertContains(response, "Esta acción es permanente")
        self.assertContains(response, 'aria-describedby="aviso-eliminacion"')
        self.assertContains(response, "Confirmar eliminación")
        self.assertContains(response, "Cancelar")
        self.assertContains(response, 'method="post"')
        self.assertLess(response.content.index(b">Cancelar</a>"), response.content.index(b">Confirmar"))
        self.assertTrue(Instrumento.objects.filter(pk=self.instrumento.pk).exists())

    def test_borrado_requiere_csrf_y_elimina_con_post_valido(self):
        cliente = Client(enforce_csrf_checks=True)
        url = reverse("instrumentos:eliminar", args=[self.instrumento.pk])
        confirmacion = cliente.get(url)
        token = re.search(
            r'name="csrfmiddlewaretoken" value="([^"]+)"',
            confirmacion.content.decode(confirmacion.charset),
        )
        self.assertIsNotNone(token)

        response = cliente.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Instrumento.objects.filter(pk=self.instrumento.pk).exists())

        response = cliente.post(url, {"csrfmiddlewaretoken": token.group(1)}, follow=True)
        self.assertRedirects(response, reverse("instrumentos:lista"))
        self.assertContains(response, "Instrumento eliminado correctamente.")
        self.assertFalse(Instrumento.objects.filter(pk=self.instrumento.pk).exists())


class InventarioFiltrosTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Instrumento.objects.all().delete()
        cls.bajo = Instrumento.objects.create(
            nombre="Bajo Jazz", marca="Fender", categoria="Bajos", precio=100000, stock=2,
        )
        cls.guitarra = Instrumento.objects.create(
            nombre="Guitarra Luna", marca="fender", categoria="Guitarras", precio=150000, stock=0,
        )
        cls.teclado = Instrumento.objects.create(
            nombre="Piano Claro", marca="Yamaha", categoria="Teclados", precio=200000, stock=5,
        )
        cls.bajo_sin_stock = Instrumento.objects.create(
            nombre="Bajo Jazz", marca="Yamaha", categoria="Bajos", precio=130000, stock=0,
        )

    def consultar(self, **filtros):
        return self.client.get(reverse("instrumentos:lista"), filtros)

    def test_busqueda_por_nombre_sin_distinguir_mayusculas(self):
        response = self.consultar(q="  jAzZ  ")
        self.assertQuerySetEqual(response.context["instrumentos"], [self.bajo, self.bajo_sin_stock])
        self.assertContains(response, 'name="q" value="jAzZ"')

    def test_busqueda_por_marca_incluye_grafia_historica(self):
        response = self.consultar(q="FeNd")
        self.assertQuerySetEqual(response.context["instrumentos"], [self.bajo, self.guitarra])

    def test_busqueda_de_veinte_caracteres_concuerda_con_maxlength(self):
        nombre = "Bateria" + "a" * 13
        instrumento = Instrumento.objects.create(
            nombre=nombre, marca="Yamaha", categoria="Percusion", precio=1, stock=1,
        )
        response = self.consultar(q=nombre, categoria="Percusion", disponibilidad="con")
        self.assertQuerySetEqual(response.context["instrumentos"], [instrumento])
        self.assertContains(response, 'maxlength="20"')
        self.assertContains(response, f'name="q" value="{nombre}"')

    def test_busqueda_excesiva_no_consulta_y_conserva_los_selectores(self):
        for entrada in ("A" * 21, " " * 21, "A" * 300):
            with self.subTest(entrada=entrada), self.assertNumQueries(0):
                response = self.consultar(q=entrada, categoria="Guitarras", disponibilidad="sin")
                self.assertContains(response, "La búsqueda admite un máximo de 20 caracteres.")
                self.assertContains(response, 'aria-invalid="true"')
                self.assertContains(response, 'value="Guitarras" selected')
                self.assertContains(response, 'value="sin" selected')
                self.assertNotContains(response, "No se encontraron instrumentos")
                self.assertNotContains(response, "Aún no hay instrumentos registrados")

    def test_filtro_categoria_y_opciones_reales(self):
        response = self.consultar(categoria="Bajos")
        self.assertQuerySetEqual(response.context["instrumentos"], [self.bajo, self.bajo_sin_stock])
        self.assertContains(response, '<option value="Bajos" selected>Bajos</option>', html=True)
        self.assertContains(response, '<option value="Percusion">Baterías</option>', html=True)
        self.assertEqual(
            list(response.context["categorias"]),
            [("Guitarras", "Guitarras"), ("Bajos", "Bajos"), ("Teclados", "Teclados"), ("Percusion", "Baterías")],
        )

    def test_disponibilidad_con_stock_y_sin_stock(self):
        for estado, registros in (
            ("con", [self.bajo, self.teclado]),
            ("sin", [self.bajo_sin_stock, self.guitarra]),
        ):
            with self.subTest(estado=estado):
                response = self.consultar(disponibilidad=estado)
                self.assertQuerySetEqual(response.context["instrumentos"], registros)
                self.assertContains(response, f'value="{estado}" selected')

    def test_combina_busqueda_categoria_y_disponibilidad(self):
        response = self.consultar(q="Fender", categoria="Guitarras", disponibilidad="sin")
        self.assertQuerySetEqual(response.context["instrumentos"], [self.guitarra])
        self.assertContains(response, 'name="q" value="Fender"')
        self.assertContains(response, 'value="Guitarras" selected')
        self.assertContains(response, 'value="sin" selected')

    def test_ignora_opciones_invalidas_sin_descartar_la_busqueda(self):
        response = self.consultar(q="Piano", categoria="Otra", disponibilidad="negativo")
        self.assertQuerySetEqual(response.context["instrumentos"], [self.teclado])
        self.assertEqual(response.context["categoria_seleccionada"], "")
        self.assertEqual(response.context["disponibilidad"], "")

    def test_distingue_inventario_vacio_de_busqueda_sin_resultados(self):
        response = self.consultar(q="Sin coincidencias")
        self.assertContains(response, "No se encontraron instrumentos con los criterios seleccionados")
        self.assertNotContains(response, "Aún no hay instrumentos registrados")
        self.assertContains(
            response,
            f'<a class="inventario-enlace" href="{reverse("instrumentos:lista")}">limpia los filtros</a>',
            html=True,
        )
        Instrumento.objects.all().delete()
        response = self.consultar(q="Sin coincidencias")
        self.assertContains(response, "Aún no hay instrumentos registrados")
        self.assertNotContains(response, "No se encontraron instrumentos con los criterios seleccionados")

    def test_limpiar_filtros_restaura_el_listado_alfabetico_con_desempate_por_id(self):
        response = self.consultar(categoria="Teclados")
        lista = reverse("instrumentos:lista")
        self.assertContains(
            response, f'<a class="inventario-enlace" href="{lista}">Limpiar filtros</a>', html=True,
        )
        response = self.client.get(lista)
        self.assertQuerySetEqual(
            response.context["instrumentos"], [self.bajo, self.bajo_sin_stock, self.guitarra, self.teclado],
        )

    def test_inventario_enlaza_a_las_cuatro_operaciones_crud(self):
        response = self.consultar(q="Fender", disponibilidad="con")
        for nombre, args in (
            ("crear", ()), ("detalle", (self.bajo.pk,)), ("editar", (self.bajo.pk,)),
            ("eliminar", (self.bajo.pk,)),
        ):
            with self.subTest(nombre=nombre):
                ruta = reverse(f"instrumentos:{nombre}", args=args)
                self.assertContains(response, f'href="{ruta}"')
                self.assertEqual(self.client.get(ruta).status_code, 200)
        self.assertEqual(Instrumento.objects.count(), 4)


class PrecioCLPTests(SimpleTestCase):
    def test_analizador_convierte_sin_redondear(self):
        for entrada, esperado in (
            ("1", 1), ("1000", 1000), ("100000", 100000), ("$100.000", 100000),
            ("1.000", 1000), ("999999", 999999), ("$999.999", 999999),
        ):
            with self.subTest(entrada=entrada):
                self.assertEqual(analizar_precio(entrada), esperado)

    def test_analizador_rechaza_importes_ambiguos(self):
        for entrada in (
            "", "0", "1000000", "9999999", "$9.999.999", "-100", "1.50", "1,50", "1e3", "abc",
            "$1.00.0", "12.345.678", "00000001", "١٠٠",
        ):
            with self.subTest(entrada=entrada):
                with self.assertRaises(ValidationError):
                    analizar_precio(entrada)


class ValidacionesInstrumentoTests(TestCase):
    datos = {
        **InstrumentoCRUDTests.datos,
        "precio": 100000,
    }

    @classmethod
    def setUpTestData(cls):
        Instrumento.objects.all().delete()
        cls.instrumento = Instrumento.objects.create(**cls.datos)

    def rutas_crud(self):
        return (
            reverse("instrumentos:crear"),
            reverse("instrumentos:editar", args=[self.instrumento.pk]),
        )

    def test_selectores_de_alta_y_edicion_ofrecen_solo_las_opciones_definitivas(self):
        for ruta in self.rutas_crud():
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)
                campos = respuesta.context["formulario"].fields
                self.assertEqual(
                    [valor for valor, _ in campos["marca"].choices if valor],
                    ["Fender", "Gibson", "Yamaha", "Roland", "Ibanez"],
                )
                self.assertEqual(
                    [(valor, etiqueta) for valor, etiqueta in campos["categoria"].choices if valor],
                    [("Guitarras", "Guitarras"), ("Bajos", "Bajos"), ("Teclados", "Teclados"), ("Percusion", "Baterías")],
                )

    def test_todas_las_marcas_estan_disponibles_en_cada_categoria(self):
        for marca, _ in Instrumento.MARCAS:
            for categoria, _ in Instrumento.CATEGORIAS:
                with self.subTest(marca=marca, categoria=categoria):
                    formulario = InstrumentoForm({**self.datos, "marca": marca, "categoria": categoria})
                    self.assertTrue(formulario.is_valid(), formulario.errors)

    def test_editar_marca_actualiza_el_acabado_sin_alterar_el_precio(self):
        _, editar = self.rutas_crud()
        respuesta = self.client.get(editar)
        self.assertContains(respuesta, 'style="--acabado: #CF3434"')
        self.assertEqual(respuesta.context["colores_marca"], {
            "Fender": "#CF3434", "Gibson": "#2975CD", "Yamaha": "#232323",
            "Roland": "#F1F0E9", "Ibanez": "#8650C0",
        })
        respuesta = self.client.post(editar, {**self.datos, "marca": "Roland"})
        self.assertRedirects(respuesta, reverse("instrumentos:lista"))
        self.instrumento.refresh_from_db()
        self.assertEqual(self.instrumento.marca, "Roland")
        self.assertEqual(self.instrumento.precio, self.datos["precio"])
        self.assertContains(self.client.get(editar), 'style="--acabado: #F1F0E9"')

    def test_create_y_update_rechazan_los_mismos_valores(self):
        invalidos = {
            "nombre": ("", "A", "A" * 21, "12345", "Bajo 2", "   ", "--", "Bajo!", "Ba\tjo"),
            "marca": ("", "Otra marca", "fender", "Casio", "Pearl"),
            "categoria": ("", "Otra categoría", "Viento", "Acusticos"),
            "precio": ("", "0", "1000000", "9999999", "-100", "1.50", "abc", "$1.00.0", "12.345.678"),
            "stock": ("", "1000", "0000", "-1", "1.0", "abc"),
            "descripcion": ("a" * 101, " " * 101),
        }
        for ruta in self.rutas_crud():
            for campo, entradas in invalidos.items():
                for entrada in entradas:
                    with self.subTest(ruta=ruta, campo=campo, entrada=entrada):
                        datos = {**self.datos, "nombre": "Bajo Jazz", campo: entrada}
                        response = self.client.post(ruta, datos)
                        self.assertContains(response, 'class="errorlist"')
                        self.assertEqual(set(response.context["formulario"].errors), {campo})
                        self.instrumento.refresh_from_db()
                        self.assertEqual(self.instrumento.nombre, self.datos["nombre"])
                        self.assertEqual(Instrumento.objects.count(), 1)

    def test_create_y_update_aceptan_limites_y_formatos(self):
        validos = {
            "nombre": (
                ("Áñ", "Áñ"), ("Á" * 20, "Á" * 20),
                ("  Guitarra    Strato  ", "Guitarra Strato"),
                ("Bajo-Eléctrico", "Bajo-Eléctrico"),
            ),
            "marca": [(marca, marca) for marca, _ in Instrumento.MARCAS],
            "categoria": [(categoria, categoria) for categoria, _ in Instrumento.CATEGORIAS],
            "precio": (
                ("1", 1), ("1000", 1000), ("100000", 100000), ("$100.000", 100000),
                ("1.000", 1000), ("999999", 999999), ("$999.999", 999999),
            ),
            "stock": (("0", 0), ("1", 1), ("999", 999)),
            "descripcion": (("", ""), ("Á1, " * 25, "Á1, " * 25)),
        }
        crear, editar = self.rutas_crud()
        for ruta in (crear, editar):
            for campo, entradas in validos.items():
                for entrada, esperado in entradas:
                    with self.subTest(ruta=ruta, campo=campo, entrada=entrada):
                        response = self.client.post(ruta, {**self.datos, campo: entrada})
                        self.assertRedirects(response, reverse("instrumentos:lista"))
                        objeto = (
                            Instrumento.objects.latest("pk") if ruta == crear
                            else Instrumento.objects.get(pk=self.instrumento.pk)
                        )
                        self.assertEqual(getattr(objeto, campo), esperado)

    def test_moneda_renderizada_y_guardada_como_entero_en_mariadb(self):
        crear, editar = self.rutas_crud()
        self.assertContains(self.client.get(editar), 'value="$100.000"')
        self.assertContains(self.client.get(crear), "Selecciona una marca")
        for ruta in (crear, editar):
            response = self.client.post(ruta, {**self.datos, "precio": "$100.000"})
            self.assertRedirects(response, reverse("instrumentos:lista"))
            pk = Instrumento.objects.latest("pk").pk if ruta == crear else self.instrumento.pk
            with connection.cursor() as cursor:
                cursor.execute("SELECT precio FROM instrumentos_instrumento WHERE id = %s", [pk])
                precio = cursor.fetchone()[0]
            self.assertIs(type(precio), int)
            self.assertEqual(precio, 100000)
            detalle = reverse("instrumentos:detalle", args=[pk])
            self.assertContains(self.client.get(detalle), "$100.000 CLP")
        self.assertContains(self.client.get(reverse("instrumentos:lista")), "$100.000 CLP")

    def test_edicion_muestra_marca_historica_con_grafia_del_catalogo(self):
        Instrumento.objects.filter(pk=self.instrumento.pk).update(marca="fender")
        response = self.client.get(self.rutas_crud()[1])
        self.assertContains(response, '<option value="Fender" selected>Fender</option>', html=True)
        self.instrumento.refresh_from_db()
        self.assertEqual(self.instrumento.marca, "fender")

    def test_estados_de_stock_en_catalogo_y_detalle(self):
        rutas = (
            reverse("instrumentos:lista"),
            reverse("instrumentos:detalle", args=[self.instrumento.pk]),
        )
        for stock, estado in ((0, "Sin stock"), (1, "Stock bajo"), (2, "Stock bajo"), (3, "Disponible")):
            with self.subTest(stock=stock):
                Instrumento.objects.filter(pk=self.instrumento.pk).update(stock=stock)
                for ruta in rutas:
                    self.assertContains(self.client.get(ruta), estado)

    def test_create_y_update_renderizan_limites_nativos(self):
        for ruta in self.rutas_crud():
            with self.subTest(ruta=ruta):
                response = self.client.get(ruta)
                self.assertContains(response, "instrumentos/js/validaciones.js")
                contenido = response.content.decode(response.charset)
                self.assertRegex(contenido, r'name="precio"[^>]*data-precio-clp=""[^>]*data-max-digitos="6"')
                self.assertRegex(contenido, r'name="stock"[^>]*data-error-stock="[^"]+"[^>]*data-max-digitos="3"')
                self.assertRegex(contenido, r'name="nombre"[^>]*minlength="2"[^>]*maxlength="20"')
                for nombre, etiqueta, limite in (
                    ("nombre", "input", 20), ("stock", "input", 3),
                    ("descripcion", "textarea", 100),
                ):
                    control = re.search(rf'<{etiqueta} [^>]*name="{nombre}"[^>]*>', contenido)
                    self.assertIsNotNone(control)
                    self.assertIn(f'maxlength="{limite}"', control.group())
                    if etiqueta == "input":
                        self.assertIn('type="text"', control.group())

    def test_mariadb_bloquea_escrituras_directas_fuera_de_limite(self):
        for cambio in (
            {"precio": 0}, {"precio": 1000000}, {"stock": 1000},
            {"nombre": "A"}, {"descripcion": "a" * 101},
        ):
            with self.subTest(cambio=cambio):
                with self.assertRaises(IntegrityError), transaction.atomic():
                    Instrumento.objects.filter(pk=self.instrumento.pk).update(**cambio)
