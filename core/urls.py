from django.urls import path
from . import views # Importe o módulo completo para facilitar
from .views import index, about, contato, login, selecionar_paciente_exame, criar_anamnese_rapida, \
    cadastro_anamnese, consulta_anamnese, excluir_anamnese, gerar_pdf_anamnese, cadastro_exame_fisico, \
    excluir_exame_fisico, gerenciar_exames, gerar_pdf_exame_individual, dashboard, selecionar_paciente_anamnese, \
    pagina_vendas, webhook_mercado_pago, estudo_flashcards, criar_flashcard, responder_flashcard, dashboard_flashcards

urlpatterns = [
    # --- PÁGINAS PÚBLICAS ---
    path('', index, name='index'),
    path('about/', about, name='about'),
    path('contato/', contato, name='contato'),
    #path('cadastro/', cadastro, name='cadastro'),
    #path('login/', login, name='login'),

    # --- DASHBOARD ---
    path('dashboard/', dashboard, name='dashboard'),

    # --- GESTÃO DE PACIENTES (NOVO) ---
    # Agora centralizamos a busca e seleção aqui

    #path('pacientes/criar-rapido/', criar_anamnese_rapida, name='criar_anamnese_rapida'),
    #path('pacientes/exame/', selecionar_paciente_exame, name='selecionar_paciente_exame'),
    #path('pacientes/anamnese/', selecionar_paciente_anamnese, name='selecionar_paciente_anamnese'),


    # --- ANAMNESES (VINCULADAS AO PACIENTE) ---
    # Note que agora o ideal é passar o paciente_id para uma nova anamnese
    #path('paciente/<int:paciente_id>/anamnese/nova/', cadastro_anamnese, name='cadastro_anamnese'),
    #path('anamnese/editar/<int:pk>/', cadastro_anamnese, name='editar_anamnese'),
    #path('anamnese/consultar/', consulta_anamnese, name='consulta_anamnese'),
    #path('anamnese/excluir/<int:pk>/', excluir_anamnese, name='excluir_anamnese'),
    #path('anamnese/pdf/<int:pk>/', gerar_pdf_anamnese, name='gerar_pdf_anamnese'),

    # --- EXAMES FÍSICOS (VINCULADOS À ANAMNESE) ---
    #path('exame-fisico/novo/', cadastro_exame_fisico, name='cadastro_exame_fisico'),
    #path('exame-fisico/editar/<int:pk>/', cadastro_exame_fisico, name='editar_exame_fisico'),
    #path('exame-fisico/excluir/<int:pk>/', excluir_exame_fisico, name='excluir_exame_fisico'),
    #path('exames-fisicos/historico/',gerenciar_exames, name='gerenciar_exames'),
    #path('exame-fisico/gerenciar/<int:anamnese_id>/', gerenciar_exames, name='gerenciar_exames'),
    #path('exame-fisico/pdf/<int:exame_id>/', gerar_pdf_exame_individual, name='gerar_pdf_exame_individual'),

    #VENDAS E FINANÇAS
    path('vendas/', pagina_vendas, name='pagina_vendas'),
    path('webhook/mercadopago/', webhook_mercado_pago, name='processar_pagamento'),

    #FLASHCARDS
    path('flashcards/estudo/', estudo_flashcards, name='estudo_flashcards'),
    path('flashcards/novo/', criar_flashcard, name='criar_flashcard'),
    path('flashcards/responder/<int:card_id>/', responder_flashcard, name='responder_card'),
    path('flashcards/dashboard/', dashboard_flashcards, name='dashboard_flashcards'),

    #CURSO
    path('curso/aula/<int:aula_id>/', views.visualizacao_aula, name='visualizacao_aula'),
    path('curso/aula/concluir/<int:aula_id>/', views.marcar_concluida, name='marcar_concluida'),
    path('curso/', views.indice_curso, name='indice_curso'),

    #QUESTÕES
    path('questoes/', views.banco_questoes, name='banco_questoes'), # ESSENCIAL

]
