from urllib.parse import urlencode

from django import template

register = template.Library()


@register.filter
def make_list(value):
    """Converte uma string em lista de caracteres."""
    return list(str(value))


@register.simple_tag
def querystring(params, **kwargs):
    """Adiciona ou substitui parâmetros na query string."""
    query = dict(params)
    query.update(kwargs)
    query = {k: v for k, v in query.items() if v}
    return urlencode(query)
