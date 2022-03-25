from django import template
from datetime import date, timedelta

register = template.Library()


@register.filter(name='nbsp')
def nbsp(value):
    return value.replace("&nbsp;", " ")


@register.filter(name='zakat')
def zakat(value):
    try:
        return float(value) / 40
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter(name='share')
def share(value, index):
    try:
        index = index + 1
        return int(value * index)
    except (ValueError, ZeroDivisionError):
        return 0
