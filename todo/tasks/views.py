from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.apps import apps
from django.http import HttpResponseNotFound, HttpRequest
from django.forms import modelform_factory, ModelForm, widgets
from django.shortcuts import render
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


class TaskCreateView(View):
    types = "onetime"
    template_name = "tasks/task/create.html"

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

        # Переробити через супер.діспатч, пофіксити МРО.

    def get(self, request:HttpRequest, task_type:str):
        task_form = TaskForm()
        task_type_form = self.form_class()
        return render(
            request,
            self.template_name,
            context={"task_form": task_form, "form": task_type_form, "model": self.model},
        )
    
    def post(self, request:HttpRequest, task_type:str):
        task_form = TaskForm(request.POST)
        task_type_form = self.form_class(request.POST)
        if task_form.is_valid() and task_type_form.is_valid():
            print('q')
            print(task_type_form.cleaned_data)
            ...
        return render(
            request,
            self.template_name,
            context={"task_form": task_form, "form": task_type_form, "model": self.model}
        )
