from decimal import Decimal, InvalidOperation

from django import template

register = template.Library()


@register.filter
def brl(value):
    if value is None or value == '':
        return 'R$ 0,00'
    try:
        value = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return 'R$ 0,00'
    negative = value < 0
    value = abs(value)
    cents = value % 1
    integer_part = int(value)
    cents_str = f'{cents:.2f}'[2:]
    int_str = f'{integer_part:,}'.replace(',', '.')
    formatted = f'R$ {int_str},{cents_str}'
    if negative:
        formatted = f'-{formatted}'
    return formatted