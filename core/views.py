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
from django.utils import timezone
import io
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Anamnese, ExameFisico



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


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Anamnese, ExameFisico

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Anamnese, ExameFisico


def cadastro_exame_fisico(request, pk=None):
    # Lógica de Inicialização: Edição ou Novo Registro
    if pk:
        exame = get_object_or_404(ExameFisico, pk=pk)
        anamnese = exame.anamnese
    else:
        exame = None
        anamnese_id = request.GET.get('vinculo')
        if not anamnese_id:
            messages.error(request, "Vínculo de anamnese não encontrado.")
            return redirect('consulta_anamnese')
        anamnese = get_object_or_404(Anamnese, id=anamnese_id)

    if request.method == 'POST':
        tipo = request.POST.get('tipo_exame')

        if not exame:
            exame = ExameFisico(anamnese=anamnese)

        exame.tipo_exame = tipo

        # --- 1. SE FOR EXAME GERAL ---
        if tipo == 'geral':
            exame.estado_geral = request.POST.get('eg_estado')
            exame.nivel_consciencia = request.POST.get('eg_consciencia')
            exame.hidratacao = request.POST.get('eg_hidratacao')
            exame.mucosas = request.POST.get('eg_mucosas')
            exame.pele_anexos = request.POST.get('eg_pele_anexos')
            exame.movimentos_involuntarios = request.POST.get('eg_mov_inv')
            exame.desenvolvimento_fisico = request.POST.get('eg_desenv')
            exame.estado_nutricional = request.POST.get('eg_nutricional')
            exame.musculatura = request.POST.get('eg_musculatura')
            exame.veias_superficiais = request.POST.get('eg_veias')
            exame.veias_obs = request.POST.get('eg_veias_obs')
            exame.circulacao_colateral = request.POST.get('eg_circ_colat')
            exame.edema = request.POST.get('eg_edema')
            exame.fala_linguagem = request.POST.get('eg_fala')
            exame.marcha = request.POST.get('eg_marcha')

            # Tratamento de decimais
            exame.peso = request.POST.get('eg_peso', '').replace(',', '.') or None
            exame.altura = request.POST.get('eg_altura') or None
            exame.imc = request.POST.get('eg_imc', '').replace(',', '.') or None
            exame.temperatura = request.POST.get('eg_temp', '').replace(',', '.') or None

        # --- 2. SE FOR AVALIAÇÃO NUTRICIONAL (PORTO) ---
        elif tipo == 'nutricional':
            exame.peso_habitual = request.POST.get('peso_habitual', '').replace(',', '.') or None
            exame.perdeu_peso_6_meses = request.POST.get('perdeu_peso_6_meses')
            exame.quantidade_perdida_kg = request.POST.get('quantidade_perdida_kg', '').replace(',', '.') or None

            perc = request.POST.get('percentual_perda', '').replace('%', '').replace(',', '.')
            exame.percentual_perda = perc if perc else None

            exame.ingestao_alimentar = request.POST.get('ingestao_alimentar')
            exame.dieta_tipo = request.POST.get('dieta_tipo')
            exame.demanda_metabolica = request.POST.get('demanda_metabolica')
            exame.perda_gordura_subcutanea = request.POST.get('perda_gordura_subcutanea') or 0
            exame.perda_muscular = request.POST.get('perda_muscular') or 0
            exame.ascite = request.POST.get('ascite') or 0
            exame.classificacao_nutricional = request.POST.get('classificacao_nutricional')

        # --- 3. SE FOR SINTOMA DOR (NOVO) ---
        elif tipo == 'dor':
            exame.localizacao_dor = request.POST.get('localizacao_dor')
            exame.intensidade_dor = request.POST.get('intensidade_dor')
            exame.qualidade_carater = request.POST.get('qualidade_carater')
            exame.duracao_dor = request.POST.get('duracao_dor')
            exame.frequencia_dor = request.POST.get('frequencia_dor')
            exame.irradiacao_dor = request.POST.get('irradiacao_dor')
            exame.fatores_agravantes = request.POST.get('fatores_agravantes')
            exame.fatores_atenuantes = request.POST.get('fatores_atenuantes')
            exame.sintomas_associados_dor = request.POST.get('sintomas_associados_dor')

        # --- 4. SE FOR PRESSÃO ARTERIAL (PORTO) ---
        elif tipo == 'pressao_arterial':
            # Identificação básica [cite: 33]
            exame.tipo_esfigmomanometro = request.POST.get('tipo_esfigmomanometro')  # [cite: 35]

            # Avaliação de rotina (Sentado/Deitado) [cite: 37, 38]
            exame.pa_sentado_sistolica = request.POST.get('pa_sentado_sistolica')
            exame.pa_sentado_diastolica = request.POST.get('pa_sentado_diastolica')

            # Pesquisa de Hipotensão Ortostática [cite: 41]
            # Deitado (mínimo 5 min) [cite: 42, 43, 44]
            exame.pa_deitado_sistolica = request.POST.get('pa_deitado_sistolica')
            exame.pa_deitado_diastolica = request.POST.get('pa_deitado_diastolica')
            exame.fc_deitado = request.POST.get('fc_deitado')

            # De pé (após 1 a 3 min) [cite: 39, 45, 46, 47]
            exame.pa_em_pe_sistolica = request.POST.get('pa_em_pe_sistolica')
            exame.pa_em_pe_diastolica = request.POST.get('pa_em_pe_diastolica')
            exame.fc_em_pe = request.POST.get('fc_em_pe')

        # --- PARA OUTROS TIPOS / DESCRIÇÃO LIVRE ---
        else:
            exame.descricao_exame = request.POST.get('descricao_exame')

        exame.save()
        messages.success(request, "Registro clínico atualizado com sucesso!")
        return redirect('gerenciar_exames', anamnese_id=anamnese.id)

    return render(request, 'cadastro_exame_fisico.html', {
        'exame': exame,
        'anamnese': anamnese,
        'tipos_opcoes': ExameFisico.TIPOS_EXAME
    })

    return render(request, 'cadastro_exame_fisico.html', context)
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


def render_to_pdf(template_src, context_dict={}):
    # Renderiza o HTML como string
    html_string = render_to_string(template_src, context_dict)

    # Cria o PDF
    html = HTML(string=html_string, base_url=None)  # base_url ajuda a encontrar imagens/css
    result = html.write_pdf()

    # Retorna o Response
    response = HttpResponse(result, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio.pdf"'
    return response


def gerar_pdf_anamnese(request, pk):
    anamnese = get_object_or_404(Anamnese, pk=pk)
    exames_vinculados = anamnese.exames_fisicos.all().order_by('-data_exame')

    context = {
        'anamnese': anamnese,
        'exames': exames_vinculados,
        'data_impressao': timezone.now(),
        'usuario_nome': request.user.get_full_name() or request.user.username, # Passa o nome aqui
    }
    return render_to_pdf('pdf_anamnese.html', context)

def gerar_pdf_exame_individual(request, exame_id):
    exame = get_object_or_404(ExameFisico, id=exame_id)
    context = {
        'anamnese': exame.anamnese,
        'exames': [exame],
        'data_impressao': timezone.now(),
        'usuario_nome': request.user.get_full_name() or request.user.username, # Passa o nome aqui
    }
    return render_to_pdf('pdf_anamnese.html', context)



def gerar_pdf_exames_lista(request, anamnese_id, exame_id=None):
    anamnese = get_object_or_404(Anamnese, id=anamnese_id)

    if exame_id:
        # Imprime apenas um exame específico
        exames = ExameFisico.objects.filter(id=exame_id)
    else:
        # Imprime todos os exames daquela anamnese
        exames = anamnese.exames_fisicos.all().order_by('-data_exame')

    context = {
        'anamnese': anamnese,
        'exames': exames,
        'data_impressao': timezone.now()
    }
    return render_to_pdf('pdf_exames.html', context)



