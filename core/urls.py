from django.urls import path
from .views import index, about, cadastro, login, cadastro_anamnese

urlpatterns = [
    path('',index, name='index'),
    path('about',about, name='about'),
    path('cadastro',cadastro, name='cadastro'),
    path('login',login, name='login'),
    path('cadastro_anamnese',cadastro_anamnese, name='cadastro_anamnese'),
]