from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ContatoForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Anamnese, ExameFisico
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import tempfile



def index (request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def cadastro(request):
    return render(request, 'cadastro.html')

def login(request):
    return render(request, 'login.html')


@login_required
def cadastro_anamnese(request, pk=None):
    # Se houver PK, busca a anamnese existente; se não, cria uma instância vazia (None)
    anamnese = get_object_or_404(Anamnese, pk=pk) if pk else None

    if request.method == 'POST':
        # Coletamos os dados do POST
        # Usamos request.POST.get('campo', anamnese.campo if anamnese else '') para manter dados se houver erro

        campos = [
            'nome', 'idade', 'estado_civil', 'endereco', 'religiao', 'etnia',
            'profissao', 'plano_saude', 'queixa_principal', 'hma', 'is_geral',
            'is_respiratorio', 'is_cardiovascular', 'is_digestorio',
            'gestacao_nascimento', 'desenvolvimento_neural', 'puberdade',
            'menarca_idade', 'menopausa_idade', 'sexarca_idade', 'orientacao_sexual',
            'doencas_infancia', 'traumas', 'alergias', 'doencas_cronicas',
            'cirurgias_transfusoes', 'medicamentos', 'gesta', 'para', 'aborto',
            'vacinas', 'antecedentes_familiares', 'alimentacao_peso',
            'atividades_fisicas', 'ocupacoes', 'viagens', 'atividade_sexual',
            'tabaco', 'alcool', 'outras_drogas', 'moradia_saneamento',
            'condicoes_economicas', 'ajustamento_familiar', 'contato_doentes'
        ]

        # Se estamos editando, atualizamos o objeto existente
        if anamnese:
            for campo in campos:
                setattr(anamnese, campo, request.POST.get(campo))
            anamnese.save()
        else:
            # Se for novo, criamos um dicionário com os dados e o usuário
            dados_anamnese = {campo: request.POST.get(campo) for campo in campos}
            dados_anamnese['usuario'] = request.user
            anamnese = Anamnese.objects.create(**dados_anamnese)

        return render(request, 'cadastro_anamnese.html', {
            'abrir_modal_exame': True,
            'anamnese_id': anamnese.id,
            'anamnese': anamnese  # Passamos de volta para manter os dados na tela
        })

    return render(request, 'cadastro_anamnese.html', {'anamnese': anamnese})


def consulta_anamnese(request):
    # Captura o termo de busca enviado via campo 'q' no HTML
    termo_busca = request.GET.get('q')

    if termo_busca:
        # Filtra por nome (case-insensitive) OU profissão
        listagem = Anamnese.objects.filter(
            Q(nome__icontains=termo_busca) | Q(profissao__icontains=termo_busca)
        ).order_by('-data_criacao')
    else:
        # Se não houver busca, mostra todos os registros mais recentes primeiro
        listagem = Anamnese.objects.all().order_by('-data_criacao')

    return render(request, 'consulta_lista.html', {'anamneses': listagem, 'termo': termo_busca})

def excluir_anamnese(request, pk):
    anamnese = get_object_or_404(Anamnese, pk=pk)

    # Verifica se existe um ExameFisico vinculado
    if hasattr(anamnese, 'exame_fisico') and anamnese.exame_fisico is not None:
        messages.error(request, "Não é possível excluir: existe um Exame Físico vinculado a esta anamnese.")
    else:
        anamnese.delete()
        messages.success(request, "Anamnese excluída com sucesso.")

    return redirect('consulta_lista')

def dashboard(request):
    return render(request, 'dashboard.html')

def contato(request):
    if request.method == 'POST':
        formulario = ContatoForm(request.POST)
        if formulario.is_valid():
            formulario.send_email()
            messages.success(request, 'Sua mensagem foi enviada com sucesso!')
            return redirect('contato')
        else:
            print(formulario.errors.as_data())
            messages.error(request, 'Erro ao enviar email. Verifique os campos.')
    else:
        formulario = ContatoForm()

    context = {'form': formulario}
    return render(request, 'contato.html', context)


def cadastro_exame_fisico(request, pk=None):
    # Se houver pk, estamos editando. Caso contrário, novo exame.
    exame = get_object_or_404(ExameFisico, pk=pk) if pk else None

    # Se for novo, precisamos saber a qual anamnese ele pertence via URL (?vinculo=ID)
    anamnese_id = request.GET.get('vinculo')
    anamnese = get_object_or_404(Anamnese, id=anamnese_id) if anamnese_id else (exame.anamnese if exame else None)

    if request.method == 'POST':
        descricao = request.POST.get('descricao_exame')

        if exame:
            exame.descricao_exame = descricao
            exame.save()
        else:
            ExameFisico.objects.create(
                anamnese=anamnese,
                descricao_exame=descricao
            )

        return redirect('gerenciar_exames', anamnese_id=anamnese.id)

    return render(request, 'cadastro_exame_fisico.html', {
        'exame': exame,
        'anamnese': anamnese
    })

def gerenciar_exames(request, anamnese_id):
    anamnese = get_object_or_404(Anamnese, id=anamnese_id)
    exames = anamnese.exames_fisicos.all()
    return render(request, 'gerenciar_exames.html', {'anamnese': anamnese, 'exames': exames})

def excluir_exame_fisico(request, pk):
    exame = get_object_or_404(ExameFisico, pk=pk)
    anamnese_id = exame.anamnese.id
    exame.delete()
    # Importante: adicione messages no topo: from django.contrib import messages
    messages.success(request, "Exame físico removido com sucesso!")
    return redirect('gerenciar_exames', anamnese_id=anamnese_id)


def gerar_pdf_anamnese(request, pk):
    anamnese = get_object_or_404(Anamnese, pk=pk)

    # Buscamos também os exames físicos vinculados para o relatório completo
    exames = anamnese.exames_fisicos.all()

    # Passamos o request no contexto para o template conseguir ler 'request.user'
    context = {
        'anamnese': anamnese,
        'exames': exames,
        'request': request,  # <--- Esta linha resolve o erro
    }

    html_string = render_to_string('pdf_anamnese.html', context)

    # Geramos o PDF
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="anamnese_{anamnese.nome}.pdf"'

    return response
