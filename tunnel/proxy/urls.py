from django.urls import path
from . import views

urlpatterns = [
    path('connect', views.connect),
    path('recv', views.recv),
    path('send', views.send),
    path('close', views.close),
    path('test', views.test),
]
