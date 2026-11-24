import re

from django.core.exceptions import ValidationError


NOMBRE_MIN = 2
NOMBRE_MAX = 20
PRECIO_MAX = 999_999
PRECIO_DIGITOS = len(str(PRECIO_MAX))
STOCK_MAX = 999
STOCK_DIGITOS = len(str(STOCK_MAX))
DESCRIPCION_MAX = 100

PATRON_PRECIO = rf"\$?(?:[0-9]{{1,{PRECIO_DIGITOS}}}|[0-9]{{1,3}}\.[0-9]{{3}})"
FORMATO_PRECIO = re.compile(PATRON_PRECIO)
ERROR_NOMBRE = "Usa solo letras, espacios y guiones, con al menos una letra."


def normalizar_nombre(valor):
    return " ".join(parte for parte in valor.split(" ") if parte)


def validar_letras_nombre(valor):
    if not any(caracter.isalpha() for caracter in valor) or any(
        not caracter.isalpha() and caracter not in " -" for caracter in valor
    ):
        raise ValidationError(ERROR_NOMBRE, code="nombre_invalido")


def analizar_precio(valor):
    texto = str(valor).strip()
    if FORMATO_PRECIO.fullmatch(texto):
        digitos = texto.removeprefix("$").replace(".", "")
        if 1 <= int(digitos) <= PRECIO_MAX:
            return int(digitos)
    raise ValidationError(ERROR_PRECIO, code="precio_invalido")


def formatear_clp(precio):
    return f"${precio:,}".replace(",", ".")


ERROR_PRECIO = f"Ingresa un precio entero entre $1 y {formatear_clp(PRECIO_MAX)} (por ejemplo, $100.000)."
