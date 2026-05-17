from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers


class TaskObjectField(serializers.DictField):
    def __init__(self, serializers=None, **kwargs):
        self.serializers = serializers or {}
        super().__init__(**kwargs)

    def to_representation(self, value):
        serializer = self.serializers.get(type(value))
        if not serializer:
            raise serializers.ValidationError("Incorrect task type")
        return serializer(value).data


class TaskTypeField(serializers.CharField):
    def to_representation(self, value: ContentType):
        return value.model

    def to_internal_value(self, data):
        try:
            ct = ContentType.objects.get(model=data)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError("Incorrect content_type name")
        return ct
