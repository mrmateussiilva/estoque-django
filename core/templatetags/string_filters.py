from django import template

register = template.Library()


@register.filter
def make_list(value):
    """Converte uma string em lista de caracteres."""
    return list(str(value))
