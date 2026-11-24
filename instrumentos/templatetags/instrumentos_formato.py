from django import template

from instrumentos.validaciones import formatear_clp


register = template.Library()
register.filter("clp", formatear_clp)
