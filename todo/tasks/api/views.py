from logging import getLogger
from rest_framework import permissions, viewsets, response
from rest_framework.decorators import action
from tasks.models import Task, OneTime, Recurring, RecurringStateHistory
from tasks.services.api import TaskList
from .serializers import (
    TaskSerializer,
    TaskStatusSerializer,
    HistorySerializer,
    RecurringSerializer,
    OneTimeSerializer,
)

logger = getLogger(__name__)


# add js optimization(pagination)
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    task_list = TaskList()

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    #add so unactive cannot become completed
    @action(methods=["post"], detail=True, serializer_class=TaskStatusSerializer)
    def mark_completed(self, request, pk=None):
        task = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            task.content_object.mark_completed(**data)
            return response.Response(data)
        return response.Response(serializer.errors)

    @action(methods=["get"], detail=False)
    def get_category(self, request):
        category = request.GET.get("cat")
        if not category:
            return response.Response(
                "You need to add GET param cat=*category that you need*"
            )
        filter_method = self.task_list.filters.get(category)
        if not filter_method:
            return response.Response("This category does not exist")
        tasks: dict = filter_method(self.get_queryset())
        data = []
        data.extend(OneTimeSerializer(tasks.get("onetime"), many=True).data)
        data.extend(RecurringSerializer(tasks.get("recurring"), many=True).data)
        data.extend(HistorySerializer(tasks.get("history"), many=True).data)
        return response.Response(data=data)
