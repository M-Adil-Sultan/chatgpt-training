from django import template

register = template.Library()

@register.simple_tag
def initialize(value):
    return value

@register.simple_tag(takes_context=True)
def increment(context, key):
    if key in context:
        x= x+1
        context[key] += 1
        print(f"This is meee {x}")
    else:
        context[key] = 1
        x= x+2
        print(f"This is also meee {x}")
        
    return ''