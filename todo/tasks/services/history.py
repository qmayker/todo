from django.http import HttpRequest
from django.db.models import QuerySet
from django.shortcuts import render
from tasks.models import RecurringStateHistory


class HistoryDetail:
    template_name = "tasks/history/detail.html"
    model = RecurringStateHistory

    def __init__(self, qs: QuerySet[RecurringStateHistory]):
        self.qs = qs

    def get_object(self, pk: int):
        return self.qs.get(id=pk)

    def get(self, request: HttpRequest, pk: int, history_pk: int):
        obj = self.get_object(pk=history_pk)
        return render(
            request=request,
            template_name=self.template_name,
            context={"object": obj},
        )

    @classmethod
    def get_queryset(cls, request: HttpRequest):
        queryset = cls.model.objects.get_detail_qs(user=request.user)
        return queryset
