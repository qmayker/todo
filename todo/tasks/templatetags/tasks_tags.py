from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag()
def get_model_name(object):
    return object._meta.model_name

@register.filter()
def get_path(value):
    return settings.TASK_TYPE_PATH + f'{value}.html'