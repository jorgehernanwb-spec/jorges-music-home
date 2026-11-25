from django import forms

from .models import Instrumento
from .validaciones import (
    DESCRIPCION_MAX,
    ERROR_NOMBRE,
    ERROR_PRECIO,
    NOMBRE_MAX,
    NOMBRE_MIN,
    PATRON_PRECIO,
    PRECIO_DIGITOS,
    PRECIO_MAX,
    STOCK_DIGITOS,
    STOCK_MAX,
    analizar_precio,
    formatear_clp,
    normalizar_nombre,
)

ERROR_STOCK = f"Ingresa un stock entero entre 0 y {STOCK_MAX}, con hasta tres dígitos."


class PrecioCLPField(forms.CharField):
    def prepare_value(self, value):
        return formatear_clp(value) if isinstance(value, int) else value

    def to_python(self, value):
        texto = super().to_python(value)
        return analizar_precio(texto) if texto else None


class DescripcionField(forms.CharField):
    def to_python(self, value):
        return super().to_python(value).replace("\r\n", "\n").replace("\r", "\n")


class InstrumentoForm(forms.ModelForm):
    nombre = forms.CharField(
        strip=False,
        label="Nombre",
        widget=forms.TextInput(attrs={
            "placeholder": "Ej. Bajo Precision",
            "minlength": NOMBRE_MIN,
            "maxlength": NOMBRE_MAX,
            "data-nombre-min": NOMBRE_MIN,
            "data-nombre-max": NOMBRE_MAX,
            "data-error-nombre": ERROR_NOMBRE,
        }),
        help_text=f"Entre {NOMBRE_MIN} y {NOMBRE_MAX} caracteres. Usa letras, espacios y guiones.",
        error_messages={"required": "Ingresa el nombre del instrumento."},
    )
    marca = forms.ChoiceField(
        label="Marca",
        choices=[("", "Selecciona una marca"), *Instrumento.MARCAS],
        error_messages={
            "required": "Selecciona una marca.",
            "invalid_choice": "Selecciona una marca de la lista.",
        },
    )
    precio = PrecioCLPField(
        label="Precio (CLP)",
        widget=forms.TextInput(attrs={
            "inputmode": "numeric",
            "placeholder": "$100.000",
            "data-precio-clp": "",
            "data-max-digitos": PRECIO_DIGITOS,
            "pattern": PATRON_PRECIO,
            "data-error-precio": ERROR_PRECIO,
        }),
        help_text=f"Entre $1 y {formatear_clp(PRECIO_MAX)}, sin decimales.",
        error_messages={"required": "Ingresa el precio del instrumento."},
    )
    stock = forms.RegexField(
        regex=rf"\A[0-9]{{1,{STOCK_DIGITOS}}}\Z",
        label="Stock",
        strip=False,
        widget=forms.TextInput(attrs={
            "inputmode": "numeric",
            "maxlength": STOCK_DIGITOS,
            "pattern": f"[0-9]{{1,{STOCK_DIGITOS}}}",
            "data-error-stock": ERROR_STOCK,
            "data-max-digitos": STOCK_DIGITOS,
        }),
        help_text="Ingresa un número entero entre 0 y 999.",
        error_messages={
            "required": "Ingresa el stock del instrumento.",
            "invalid": ERROR_STOCK,
        },
    )
    descripcion = DescripcionField(
        required=False,
        strip=False,
        max_length=DESCRIPCION_MAX,
        label="Descripción",
        widget=forms.Textarea(attrs={"rows": 3, "data-contador": DESCRIPCION_MAX}),
        error_messages={
            "max_length": "La descripción no puede superar los %(limit_value)s caracteres.",
        },
    )

    class Meta:
        model = Instrumento
        fields = ["nombre", "marca", "categoria", "precio", "stock", "descripcion"]
        labels = {"categoria": "Categoría"}
        error_messages = {
            "categoria": {
                "required": "Selecciona una categoría.",
                "invalid_choice": "Selecciona una categoría de la lista.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound and self.instance.pk:
            marca_actual = self.initial.get("marca", "")
            for marca, _ in Instrumento.MARCAS:
                if marca.casefold() == marca_actual.casefold():
                    self.initial["marca"] = marca
                    break

    def clean_nombre(self):
        nombre = normalizar_nombre(self.cleaned_data["nombre"])
        if len(nombre) < NOMBRE_MIN:
            raise forms.ValidationError(
                f"El nombre debe tener al menos {NOMBRE_MIN} caracteres."
            )
        if len(nombre) > NOMBRE_MAX:
            raise forms.ValidationError(
                f"El nombre no puede superar los {NOMBRE_MAX} caracteres."
            )
        return nombre

    def clean_stock(self):
        return int(self.cleaned_data["stock"])
