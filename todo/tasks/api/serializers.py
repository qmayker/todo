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


class TaskListSerializer(ModelSerializer):
    url = SerializerMethodField()
    ct = SerializerMethodField()

    def __init__(self, instance=None, data=..., **kwargs):
        logger: Logger = kwargs.pop("logger")
        super().__init__(instance, data, **kwargs)
        self.logger = logger

    class Meta:
        model = Task
        fields = ["name", "url", "ct", "id"]

    def get_url(self, obj: Task):
        return obj.get_absolute_url()

    def get_ct(self, obj: Task):
        return obj.content_type.model

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return data


class TaskStatusSerializer(Serializer):
    completed = BooleanField()


class HistorySerializer(ModelSerializer):
    url = SerializerMethodField()
    name = SerializerMethodField()

    class Meta:
        model = RecurringStateHistory
        fields = ["id", "url", "name"]

    def get_url(self, obj: RecurringStateHistory):
        return obj.get_absolute_url()

    def get_name(self, obj: RecurringStateHistory):
        return obj.task_name


class OneTimeSerializer(ModelSerializer):
    url = SerializerMethodField()
    name = SerializerMethodField()

    class Meta:
        model = OneTime
        fields = ["url", "name", "id"]

    def get_url(self, obj: OneTime):
        return obj.task.first().get_absolute_url()

    def get_name(self, obj: OneTime):
        return obj.task.first().name


class RecurringSerializer(ModelSerializer):
    url = SerializerMethodField()
    name = SerializerMethodField()

    class Meta:
        model = Recurring
        fields = ["url", "name", "id"]

    def get_url(self, obj: OneTime):
        return obj.task.first().get_absolute_url()

    def get_name(self, obj: OneTime):
        return obj.task.first().name
