from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.apps import apps
from django.http import HttpResponseNotFound, HttpRequest
from django.forms import modelform_factory, ModelForm, widgets
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import Task
from .forms import TaskForm

# Create your views here.


class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = "tasks/task/list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        qs.filter(user=self.request.user)
        return qs


class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = "tasks/task/detail.html"

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset
    
    def get(self, request, *args, **kwargs):
        task = self.get_object()
        print(task._meta.related_objects)
        return super().get(request, *args, **kwargs)


class TaskCreateView(LoginRequiredMixin, View):
    types = "onetime"
    template_name = "tasks/task/create.html"
    success_url = reverse_lazy("tasks:list")

    def get_form(self, model) -> type[ModelForm]:
        form = modelform_factory(
            model,
            exclude=["expired", "task"],
            widgets={
                "expires_at": widgets.DateTimeInput(attrs={"type": "datetime-local"})
            },
        )
        return form

    def get_model(self, name: str):
        try:
            model = apps.get_model(app_label="tasks", model_name=name)
            return model
        except LookupError:
            return None

    def dispatch(self, request, *args, **kwargs):
        task_type = kwargs.get("task_type")
        if not task_type:
            return HttpResponseNotFound()
        model = self.get_model(task_type)
        if not model:
            return HttpResponseNotFound()
        self.model = model
        self.form_class = self.get_form(model)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, task_type: str):
        task_form = TaskForm()
        type_form = self.form_class()
        return render(
            request,
            self.template_name,
            context={
                "task_form": task_form,
                "form": type_form,
                "model": self.model,
            },
        )

    def post(self, request: HttpRequest, task_type: str):
        task_form = TaskForm(request.POST)
        type_form = self.form_class(request.POST)
        if task_form.is_valid() and type_form.is_valid():
            task = task_form.save(commit=False)
            task.user = self.request.user
            task.save()
            type_obj = type_form.save(commit=False)
            type_obj.task = task
            type_obj.save()
            messages.add_message(
                request, messages.SUCCESS, 'Task has been created'
            )
            return redirect(self.success_url)

        return render(
            request,
            self.template_name,
            context={
                "task_form": task_form,
                "form": type_form,
                "model": self.model,
            },
        )
    
    #Todo - update task, filter tasks by days. reccurence tasks
