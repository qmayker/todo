from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.urls import reverse_lazy
from abc import ABC, abstractmethod


class BaseViewService(ABC):
    template_name: str
    redirect_url = reverse_lazy('tasks:list')

    def __init__(self, qs: QuerySet, pk: int):
        self.qs = qs 
        self.pk = pk

    @property
    def object(self):
        return get_object_or_404(self.qs, pk=self.pk)
    
    @abstractmethod
    def get(self, request:HttpRequest):
        ...

    def delete(self):
        self.qs.filter(pk=self.pk).delete()

    @classmethod
    def get_queryset(cls, user):
        return cls.model.objects.get_detail_qs(user)
    

