from django.urls import path
from .views import index, about, cadastro, login, cadastro_anamnese, contato, dashboard, consulta_anamnese, \
    cadastro_exame_fisico, excluir_anamnese, gerenciar_exames, excluir_exame_fisico, gerar_pdf_anamnese

urlpatterns = [
    path('',index, name='index'),
    path('about',about, name='about'),
    path('cadastro',cadastro, name='cadastro'),
    path('login',login, name='login'),
    path('cadastro_anamnese/', cadastro_anamnese, name='cadastro_anamnese'),
    path('editar_anamnese/<int:pk>/', cadastro_anamnese, name='editar_anamnese'),
    path('consultar/', consulta_anamnese, name='consulta_anamnese'),
    path('exame-fisico/novo/', cadastro_exame_fisico, name='cadastro_exame_fisico'),
    path('exame-fisico/editar/<int:pk>/', cadastro_exame_fisico, name='editar_exame_fisico'),
    path('excluir_anamnese/<int:pk>/', excluir_anamnese, name='excluir_anamnese'),
    path('anamnese/<int:anamnese_id>/exames/', gerenciar_exames, name='gerenciar_exames'),
    path('exame-fisico/excluir/<int:pk>/', excluir_exame_fisico, name='excluir_exame_fisico'),
    path('contato',contato, name='contato'),
    path('dashboard',dashboard, name='dashboard'),
    path('anamnese/pdf/<int:pk>/', gerar_pdf_anamnese, name='gerar_pdf_anamnese'),
]