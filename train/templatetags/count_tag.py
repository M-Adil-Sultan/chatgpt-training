from django import template

register = template.Library()

@register.simple_tag
def initialize(value):
    return value

@register.simple_tag(takes_context=True)
def increment(context, key):
    if key in context:     
        context[key] += 1
    else:
        context[key] = 1
    return ''