from logging import Logger
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from rest_framework.serializers import (
    ModelSerializer,
    ValidationError,
    SerializerMethodField,
    Serializer,
    BooleanField,
)
from tasks.models import Task, OneTime, Recurring, RecurringStateHistory
from .fields import TaskTypeField, TaskObjectField


class OneTimeSerializer(ModelSerializer):
    class Meta:
        model = OneTime
        fields = ["id", "expires_at", "expired"]
        read_only_fields = ["expired", "id"]


class RecurringSerializer(ModelSerializer):
    class Meta:
        model = Recurring
        fields = "__all__"
        read_only_fields = ["duration_time"]


class TaskSerializer(ModelSerializer):
    content_object = TaskObjectField(
        serializers={OneTime: OneTimeSerializer, Recurring: RecurringSerializer}
    )
    content_type = TaskTypeField()

    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "description",
            "created",
            "updated",
            "content_type",
            "content_object",
            "user",
        ]
        read_only_fields = ["created", "updated", "user"]

    @transaction.atomic
    def create(self, validated_data: dict):
        ct: ContentType = validated_data.pop("content_type")
        content_object = validated_data.pop("content_object")
        model_class = ct.model_class()
        try:
            task_type = model_class.objects.create(**content_object)
            task = Task.objects.create(content_object=task_type, **validated_data)
        except TypeError as e:
            raise ValidationError({"detail": f"Invalid fields for {model_class}: {e}"})
        except Exception as e:
            raise ValidationError({"unknown error": f"{e}"})
        return task


class TaskStatusSerializer(Serializer):
    completed = BooleanField()


class TaskTypeSerializer(ModelSerializer):
    url = SerializerMethodField()
    name = SerializerMethodField()

    class Meta:
        fields = ["id", "url", "name"]

    def get_url(self, obj):
        return obj.get_absolute_url()

    def get_name(self, obj):
        return obj.task_name


class HistorySerializer(TaskTypeSerializer):
    class Meta(TaskTypeSerializer.Meta):
        model = RecurringStateHistory


class OneTimeSerializer(TaskTypeSerializer):
    class Meta(TaskTypeSerializer.Meta):
        model = OneTime


class RecurringSerializer(TaskTypeSerializer):
    class Meta(TaskTypeSerializer.Meta):
        model = Recurring
