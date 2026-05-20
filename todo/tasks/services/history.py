from django.http import HttpRequest
from django.db.models import QuerySet
from django.urls import reverse
from .views import BaseViewService
from django.shortcuts import render
from tasks.models import RecurringStateHistory


class HistoryViewService(BaseViewService):
    template_name = "tasks/history/detail.html"
    model = RecurringStateHistory

    def __init__(self, qs: QuerySet[RecurringStateHistory], pk: int):
        super().__init__(qs, pk)
        self.qs: QuerySet[RecurringStateHistory]

    def get(self, request: HttpRequest):
        return render(
            request=request,
            template_name=self.template_name,
            context={"object": self.object},
        )
