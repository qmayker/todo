from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('create/', views.UserCreateView.as_view(), name='create'),
]