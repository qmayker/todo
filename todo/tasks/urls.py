from django.urls import path, include
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.TaskListView.as_view(), name="list"),
    path("task/<int:pk>/", views.TaskDetailView.as_view(), name="detail"),
]
