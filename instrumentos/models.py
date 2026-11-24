
from django.db import models
from django.core.validators import (
    MinLengthValidator,
    MinValueValidator,
    MaxValueValidator,
)
from django.db.models.functions import Length
from django.db.models.lookups import GreaterThanOrEqual, LessThanOrEqual

from .validaciones import (
    DESCRIPCION_MAX,
    NOMBRE_MAX,
    NOMBRE_MIN,
    PRECIO_MAX,
    STOCK_MAX,
    validar_letras_nombre,
)


class Instrumento(models.Model):

    MARCAS = [(marca, marca) for marca in (
        "Fender", "Gibson", "Ibanez", "Yamaha", "Roland", "Casio", "Pearl",
        "Tama", "Squier", "Cort", "Korg", "Epiphone", "Otras",
    )]

    CATEGORIAS = [
        ("Guitarras", "Guitarras"),
        ("Bajos", "Bajos"),
        ("Teclados", "Teclados"),
        ("Percusion", "Baterías y percusión"),
        ("Viento", "Instrumentos de viento"),
        ("Acusticos", "Acústicos"),
    ]

    nombre = models.CharField(
        max_length=NOMBRE_MAX,
        validators=[
            MinLengthValidator(NOMBRE_MIN),
            validar_letras_nombre,
        ],
    )

    marca = models.CharField(
        max_length=20,
        choices=MARCAS,
    )

    categoria = models.CharField(
        max_length=20,
        choices=CATEGORIAS,
    )

    precio = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(PRECIO_MAX),
        ],
    )

    stock = models.PositiveIntegerField(
        validators=[MaxValueValidator(STOCK_MAX)],
    )

    descripcion = models.TextField(
        max_length=DESCRIPCION_MAX,
        blank=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(precio__gte=1, precio__lte=PRECIO_MAX),
                name="precio_clp_max_999999",
            ),
            models.CheckConstraint(
                check=models.Q(stock__gte=0, stock__lte=STOCK_MAX),
                name="stock_valido",
            ),
            models.CheckConstraint(
                check=GreaterThanOrEqual(Length("nombre"), NOMBRE_MIN),
                name="nombre_largo_minimo",
            ),
            models.CheckConstraint(
                check=LessThanOrEqual(Length("descripcion"), DESCRIPCION_MAX),
                name="descripcion_largo_100",
            ),
        ]

    def __str__(self):
        return self.nombre
