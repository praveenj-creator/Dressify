from django import template

register = template.Library()

@register.filter
def star_range(rating):
    return range(1, 6)

@register.filter
def filled_stars(rating):
    return range(int(rating))

@register.filter
def empty_stars(rating):
    return range(5 - int(rating))

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def get_item(lst, index):
    try:
        return lst[index]
    except (IndexError, TypeError):
        return ''
