from django import template

register = template.Library()


@register.filter
def table_title(title):
    return title.replace('_', ' ').upper()