from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.apps import apps
from django.http import HttpResponseNotFound, HttpRequest
from django.shortcuts import render, redirect
from django.db import transaction
from logging import Logger
from redis import Redis
from tasks.services import recurring, one_time
from .models import OneTime, Recurring, Task
from .forms import TaskForm, OneTimeForm, RecurringForm


class TaskMixin(LoginRequiredMixin, View):
    template_name = "tasks/task/create.html"
    success_url = reverse_lazy("tasks:list")
    models = ["onetime", "recurring"]
    Taskform = TaskForm
    logger : Logger
    r : Redis

    def get_form(self, model) -> type[OneTimeForm] | type[RecurringForm]:
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

    def render_forms(self, request: HttpRequest, task: Task = None):
        content_object = None
        if task:
            content_object = task.content_object
        task_form = self.Taskform(instance=task)
        type_form = self.form_class(instance=content_object)
        return render(
            request,
            self.template_name,
            context={
                "task_form": task_form,
                "form": type_form,
                "model": self.model,
            },
        )

    def validate_forms(
        self,
        request: HttpRequest,
        task_form: TaskForm,
        type_form: OneTimeForm | RecurringForm,
    ):
        if task_form.is_valid() and type_form.is_valid():
            with transaction.atomic():
                type_obj = type_form.save(commit=False)
                if isinstance(type_obj, Recurring):
                    type_obj.save()
                    state = recurring.RecurringServices.create_recurring_state(
                        obj=type_obj, changed_data=type_form.changed_data, logger=self.logger
                    )
                    service = recurring.RecurringServices(
                        obj_id=type_obj.id, logger=self.logger, r=self.r
                    )
                    eta = state.next_time
                elif isinstance(type_obj, OneTime):
                    type_obj.save()
                    service = one_time.OneTimeServices(
                        obj_id=type_obj.id, logger=self.logger, r=self.r
                    )
                    eta = type_obj.starts_at
                else:
                    raise TypeError("This task type does not exist.")
                task = task_form.save(commit=False)
                task.user = self.request.user
                task.content_object = type_obj
                task.save()
                transaction.on_commit(lambda: service.schedule_run(eta))

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
