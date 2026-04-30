from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from rest_framework.serializers import ModelSerializer, ValidationError
from tasks.models import Task, OneTime
from .fields import TaskObjectField, TaskTypeField


class TaskStatusSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = ["completed"]


class OneTimeSerializer(ModelSerializer):
    class Meta:
        model = OneTime
        fields = ["id", "expires_at", "expired"]
        read_only_fields = ["expired", "id"]


class TaskSerializer(ModelSerializer):
    content_object = TaskObjectField(serializers={OneTime: OneTimeSerializer})
    content_type = TaskTypeField()

    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "description",
            "created",
            "updated",
            "completed",
            "content_object",
            "content_type",
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
            raise ValidationError(
                {"detail": f"Invalid fields for {model_class}: {e}"}
            )
        except Exception as e:
            raise ValidationError({"unknown error": f"{e}"})
        return task
    
    #custom validate
