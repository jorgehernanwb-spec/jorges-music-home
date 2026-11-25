import re

from django.db import migrations


# Categoría interna, nombre genérico, marca, modelo, precio, stock y descripción breve.
CATALOGO = (
    ("Guitarras", "Guitarra eléctrica", "Yamaha", "Pacifica", 189990, 8,
     "guitarra eléctrica para acordes y melodías"),
    ("Guitarras", "Guitarra eléctrica", "Ibanez", "RG GIO", 279990, 6,
     "guitarra eléctrica para riffs y líneas melódicas"),
    ("Guitarras", "Guitarra eléctrica", "Fender", "Stratocaster", 489990, 4,
     "guitarra eléctrica para solos y acompañamiento"),
    ("Guitarras", "Guitarra eléctrica", "Gibson", "Les Paul", 899990, 2,
     "guitarra eléctrica para interpretar acordes y solos"),
    ("Bajos", "Bajo eléctrico", "Yamaha", "TRBX", 229990, 7,
     "bajo eléctrico para acompañamiento rítmico"),
    ("Bajos", "Bajo eléctrico", "Ibanez", "SR300", 329990, 5,
     "bajo eléctrico para líneas graves"),
    ("Bajos", "Bajo eléctrico", "Fender", "Jazz Bass", 559990, 3,
     "bajo eléctrico para acompañar un conjunto"),
    ("Bajos", "Bajo eléctrico", "Gibson", "Thunderbird", 929990, 2,
     "bajo eléctrico para la base rítmica"),
    ("Teclados", "Teclado digital", "Yamaha", "PSR-E383", 159990, 9,
     "teclado digital para practicar acordes y melodías"),
    ("Teclados", "Teclado digital", "Roland", "GO:KEYS 5", 349990, 5,
     "teclado digital para interpretación y composición"),
    ("Teclados", "Teclado digital", "Yamaha", "MX61", 459990, 4,
     "teclado digital para acompañamiento musical"),
    ("Teclados", "Teclado digital", "Roland", "JUNO-D6", 779990, 2,
     "teclado digital para interpretar melodías y armonías"),
    ("Percusion", "Batería acústica", "Yamaha", "Rydeen", 399990, 5,
     "batería acústica para práctica rítmica"),
    ("Percusion", "Batería electrónica", "Roland", "TD-02K", 499990, 4,
     "batería electrónica para practicar patrones rítmicos"),
    ("Percusion", "Batería acústica", "Yamaha", "Stage Custom", 699990, 3,
     "batería acústica para acompañar a un conjunto"),
    ("Percusion", "Batería electrónica", "Roland", "TD-07DMK", 899990, 2,
     "batería electrónica para ensayar ritmos"),
)


def cargar_catalogo(apps, schema_editor):
    Instrumento = apps.get_model("instrumentos", "Instrumento")
    instrumentos = Instrumento.objects.using(schema_editor.connection.alias)

    for categoria, nombre, marca, modelo, precio, stock, detalle in CATALOGO:
        modelo_completo = re.compile(rf"(?<!\w){re.escape(modelo)}(?!\w)", re.IGNORECASE)
        descripciones = instrumentos.filter(
            categoria=categoria, marca__iexact=marca,
        ).values_list("descripcion", flat=True)
        if any(modelo_completo.search(descripcion) for descripcion in descripciones):
            continue

        instrumentos.create(
            categoria=categoria,
            nombre=nombre,
            marca=marca,
            precio=precio,
            stock=stock,
            descripcion=f"Modelo {modelo}, {detalle}.",
        )


class Migration(migrations.Migration):
    dependencies = [("instrumentos", "0005_catalogo_categorias_marcas")]

    # Revertir borraría o dejaría sin seguimiento instrumentos ya editables por el usuario.
    operations = [migrations.RunPython(cargar_catalogo, atomic=True)]
