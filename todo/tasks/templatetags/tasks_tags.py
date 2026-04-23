from django import template

register = template.Library()

@register.simple_tag()
def get_model_name(object):
    print(object)
    return object._meta.model_name