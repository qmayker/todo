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
        print(request.data)
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data)

        if serializer.is_valid():
            serializer.save()
            print(serializer.data)
            return response.Response(serializer.data)
        print('q')
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
