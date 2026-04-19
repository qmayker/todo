from tasks.models import Task
from rest_framework.serializers import ModelSerializer, IntegerField


class TaskSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "name",
            "description",
            "created",
            "updated",
            "completed",
            "task_type",
            "user",
        ]
        read_only_fields = ["created", "updated", "user"]

class TaskStatusSerializer(ModelSerializer):
    class Meta:
        model = Task
        fields = ['completed']
