import re

from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
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

    def test_secciones_en_preparacion_son_distintas_y_marcan_la_opcion_activa(self):
        for ruta, titulo in (("coleccion", "Instrumentos"), ("mundo_musical", "Mundo musical")):
            with self.subTest(ruta=ruta):
                destino = reverse(f"instrumentos:{ruta}")
                response = self.client.get(destino)
                self.assertContains(response, f"<h1>{titulo}</h1>", html=True)
                self.assertRegex(
                    response.content.decode(),
                    rf'(?s)<a href="{destino}" aria-current="page">\s*<svg[^>]*>.*?</svg>\s*{titulo}</a>',
                )
                self.assertContains(
                    response, f'<a class="recepcion-control" href="{reverse("instrumentos:recepcion")}">Inicio</a>',
                    html=True,
                )


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
        self.assertContains(response, 'name="nombre"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

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
        response = self.client.post(url, {**self.datos, "nombre": "Bajo Jazz", "stock": 1000})
        self.assertTemplateUsed(response, "instrumentos/editar.html")
        self.assertIn("stock", response.context["formulario"].errors)
        self.assertContains(response, 'class="errorlist"')
        self.assertContains(response, 'value="Bajo Jazz"')
        self.assertContains(response, 'value="1000"')
        self.instrumento.refresh_from_db()
        for campo, dato in self.datos.items():
            self.assertEqual(getattr(self.instrumento, campo), dato)

    def test_get_muestra_confirmacion_y_no_elimina(self):
        url = reverse("instrumentos:eliminar", args=[self.instrumento.pk])
        response = self.client.get(url)
        self.assertTemplateUsed(response, "instrumentos/confirmar_eliminar.html")
        self.assertContains(response, self.instrumento.nombre)
        self.assertContains(response, "Confirmar eliminación")
        self.assertContains(response, "Cancelar")
        self.assertContains(response, 'method="post"')
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
        cls.instrumento = Instrumento.objects.create(**cls.datos)

    def rutas_crud(self):
        return (
            reverse("instrumentos:crear"),
            reverse("instrumentos:editar", args=[self.instrumento.pk]),
        )

    def test_create_y_update_rechazan_los_mismos_valores(self):
        invalidos = {
            "nombre": ("", "A", "A" * 21, "12345", "Bajo 2", "   ", "--", "Bajo!", "Ba\tjo"),
            "marca": ("", "Otra marca", "fender"),
            "categoria": ("", "Otra categoría"),
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
