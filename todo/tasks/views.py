from logging import getLogger
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.db.models import QuerySet, Q
from .mixins import TaskMixin


# Create your views here.

logger = getLogger(__name__)


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task/list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs: QuerySet[Task] = context["object_list"]
        all_tasks = qs.filter(
            Q(onetime__started=True) | Q(recurring__state__is_running=True)
        )
        context.update(
            {
                "object_all": all_tasks,
            }
        )

        return context


# add custom template to History
class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task/detail.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user).prefetch_related(
            "content_object"
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_type"] = self.object.content_object
        return context


class TaskCreateView(TaskMixin):
    logger = logger
    r = r

    def get(self, request: HttpRequest, task_type: str):
        return super().render_forms(request=self.request, task=None)

    def post(self, request: HttpRequest, task_type: str):
        task_form = self.Taskform(request.POST)
        type_form = self.form_class(request.POST)
        return super().validate_forms(
            request=request, task_form=task_form, type_form=type_form
        )


class TaskUpdateView(TaskMixin):
    logger = logger
    r = r

    def get(self, request: HttpRequest, pk: int, task_type: str):
        task = get_object_or_404(Task, id=pk)
        return super().render_forms(request=request, task=task)

    def post(self, request: HttpRequest, pk: int, task_type: str):
        task = get_object_or_404(Task, id=pk)
        task_form = self.Taskform(request.POST, instance=task)
        type_form = self.form_class(request.POST, instance=task.content_object)
        return super().validate_forms(
            request=request, task_form=task_form, type_form=type_form
        )
