from django.urls import path
from .views import index, about, produto

urlpatterns = [
    path('',index),
    path('about',about),
    path('produto',produto),
]