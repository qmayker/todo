from rest_framework import permissions, viewsets, response, status
from rest_framework.decorators import action
from django.http import HttpRequest
from tasks.models import Task
from .serializers import TaskSerializer, TaskStatusSerializer


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=["post"], detail=True, serializer_class=TaskStatusSerializer)
    def mark_completed(self, request: HttpRequest, pk=None):
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return response.Response(serializer.data)
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["get"], detail=False)
    def get_category(self, request: HttpRequest):
        category = request.GET.get("cat")
        if not category:
            return response.Response(
                "You need to add GET param cat=*category that you need*"
            )
        print(category)
        return response.Response(f"{category}")

        # validating categories + return objects by category.
