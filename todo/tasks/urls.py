from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.TaskListView.as_view(), name="list"),
    path("task/<int:pk>/", views.TaskDetailView.as_view(), name="detail"),
    path(
        "task/<int:pk>/<int:history_pk>/",
        views.TaskDetailView.as_view(),
        name="history_detail",
    ),
    path("<slug:task_type>/", views.TaskCreateView.as_view(), name="create"),
    path("<slug:task_type>/<int:pk>/", views.TaskUpdateView.as_view(), name="update"),
]
