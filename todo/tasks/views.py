from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.apps import apps
from django.http import HttpResponseNotFound, HttpRequest
from django.forms import ModelForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db.models import QuerySet, Q
from django.db import transaction
from .services.recurring import create_recurring_state
from .models import Task, OneTime, Recurring
from .forms import TaskForm, OneTimeForm, RecurringForm


# Create your views here.


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
            Q(
                onetime__expired=False,
            )
            | Q(recurring__state__is_running=True)
        )
        context.update(
            {
                "object_all": all_tasks,
            }
        )

        return context


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


class TaskCreateView(LoginRequiredMixin, View):
    types = "onetime"
    template_name = "tasks/task/create.html"
    success_url = reverse_lazy("tasks:list")
    models = ["onetime", "recurring"]

    def get_form(self, model) -> type[ModelForm]:
        if model is OneTime:
            form = OneTimeForm
        elif model is Recurring:
            form = RecurringForm
        else:
            raise ValueError("form not found")

        return form

    def get_model(self, name: str):
        try:
            model = apps.get_model(app_label="tasks", model_name=name)
            return model
        except LookupError:
            return None

    def dispatch(self, request, *args, **kwargs):
        task_type = kwargs.get("task_type")
        if task_type not in self.models:
            return HttpResponseNotFound()
        model = self.get_model(task_type)
        if not model:
            return HttpResponseNotFound()
        self.model = model
        try:
            self.form_class = self.get_form(model)
        except Exception:
            return HttpResponseNotFound()
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
            with transaction.atomic():
                type_obj = type_form.save(commit=False)
                if isinstance(type_obj, Recurring):
                    create_recurring_state(type_obj, [], change=False)
                elif isinstance(type_obj, OneTime):
                    ...
                type_obj.save()
                task = task_form.save(commit=False)
                task.user = self.request.user
                task.content_object = type_obj
                task.save()

                messages.add_message(request, messages.SUCCESS, "Task has been created")
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
