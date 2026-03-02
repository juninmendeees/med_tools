
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model  # Forma correta de chamar seu Usuario
import mercadopago
from django.conf import settings
from datetime import datetime, date, time
from weasyprint import HTML
from .models import Anamnese, ExameFisico, Paciente, Usuario, Flashcard, Modulo
from .forms import ContatoForm
import json
from .forms import FlashcardForm
from .models import Flashcard
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from .models import Modulo, Aula, ProgressoAula


def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


#def cadastro(request):
    #return render(request, 'account/signup.html')


def login(request):
    return render(request, 'login.html')

@login_required
def dashboard(request):
    # Verifica se a licença expirou ou é nula
    #if not request.user.tem_licenca_ativa():
       # return redirect('pagina_vendas')

    # Estatísticas dos Flashcards
    total_cards = Flashcard.objects.filter(Q(usuario=request.user) | Q(is_publico=True)).count()

    # Cards que vencem hoje ou já venceram
    cards_para_revisar = Flashcard.objects.filter(
        Q(usuario=request.user) | Q(is_publico=True),
        proxima_revisao__lte=timezone.now()
    ).count()

    # Cards novos (que nunca foram revisados)
    cards_novos = Flashcard.objects.filter(
        Q(usuario=request.user) | Q(is_publico=True),
        repeticoes=0
    ).count()

    context = {
        # ... seus outros contextos ...
        'fc_total': total_cards,
        'fc_revisar': cards_para_revisar,
        'fc_novos': cards_novos,
    }
    return render(request, 'dashboard.html', context)


@login_required
def cadastro_anamnese(request, pk=None, paciente_id=None):
    # 1. Busca do contexto (Edição de anamnese existente ou Nova anamnese para um paciente)
    if pk:
        # Modo Edição
        anamnese = get_object_or_404(Anamnese, pk=pk)
        paciente = anamnese.paciente
    elif paciente_id:
        # Modo Criação
        anamnese = None
        paciente = get_object_or_404(Paciente, id=paciente_id)
    else:
        # Caso de erro: redireciona para seleção
        messages.error(request, "Selecione um paciente para iniciar a anamnese.")
        return redirect('selecionar_paciente_exame')

    if request.method == 'POST':
        # Lista de campos clínicos que pertencem à tabela Anamnese
        campos = [
            'queixa_principal', 'hma', 'is_geral', 'is_respiratorio',
            'is_cardiovascular', 'is_digestorio', 'gestacao_nascimento',
            'desenvolvimento_neural', 'puberdade', 'menarca_idade',
            'menopausa_idade', 'sexarca_idade', 'orientacao_sexual',
            'doencas_infancia', 'traumas', 'alergias', 'doencas_cronicas',
            'cirurgias_transfusoes', 'medicamentos', 'gesta', 'para', 'aborto',
            'vacinas', 'antecedentes_familiares', 'alimentacao_peso',
            'atividades_fisicas', 'ocupacoes', 'viagens', 'atividade_sexual',
            'tabaco', 'alcool', 'outras_drogas', 'moradia_saneamento',
            'condicoes_economicas', 'ajustamento_familiar', 'contato_doentes'
        ]

        if anamnese:
            # Atualização de registro existente
            for campo in campos:
                setattr(anamnese, campo, request.POST.get(campo))
            anamnese.save()
        else:
            # Criação de novo registro vinculado ao paciente
            dados_anamnese = {campo: request.POST.get(campo) for campo in campos}
            dados_anamnese['paciente'] = paciente
            dados_anamnese['usuario'] = request.user
            anamnese = Anamnese.objects.create(**dados_anamnese)

        # 2. Configuração dos Sinais para o Template (Mensagens e Modais)
        messages.success(request, "Registro médico salvo com sucesso!")  #

        return render(request, 'cadastro_anamnese.html', {
            'anamnese': anamnese,
            'paciente': paciente,
            'anamnese_id': anamnese.id,
            'abrir_modal_exame': True  # Flag fundamental para o disparo do modal via JS
        })

    # Renderização inicial via GET
    return render(request, 'cadastro_anamnese.html', {
        'anamnese': anamnese,
        'paciente': paciente
    })


@login_required
def consulta_anamnese(request):
    # 1. Base da consulta com contagem de exames
    anamneses = Anamnese.objects.filter(usuario=request.user).annotate(
        total_exames=Count('exames_fisicos')
    ).order_by('-data_criacao')

    # 2. Captura de filtros do GET
    nome = request.GET.get('nome')
    cpf = request.GET.get('cpf')
    data_nasc = request.GET.get('data_nascimento')
    data_cad = request.GET.get('data_criacao')

    # 3. Aplicação de filtros lógicos
    if nome:
        anamneses = anamneses.filter(paciente__nome__icontains=nome)

    if cpf:
        anamneses = anamneses.filter(paciente__cpf__icontains=cpf)

    if data_nasc:
        # Filtro de data de nascimento simples
        anamneses = anamneses.filter(paciente__data_nascimento=data_nasc)

    if data_cad:
        try:
            # Filtro de data de criação usando range para capturar todas as horas do dia
            data_foco = datetime.strptime(data_cad, '%Y-%m-%d').date()
            inicio_dia = datetime.combine(data_foco, time.min)
            fim_dia = datetime.combine(data_foco, time.max)
            anamneses = anamneses.filter(data_criacao__range=(inicio_dia, fim_dia))
        except ValueError:
            pass

    return render(request, 'consulta_lista.html', {'anamneses': anamneses})


@login_required
def excluir_anamnese(request, pk):
    # 1. Busca a anamnese garantindo que pertence ao usuário logado
    anamnese = get_object_or_404(Anamnese, pk=pk, usuario=request.user)

    # 2. Verifica se existem exames físicos vinculados
    total_exames = anamnese.exames_fisicos.count()

    if total_exames > 0:
        # 3. Se houver exames, impede a exclusão e envia um alerta
        messages.error(
            request,
            f"Não é possível excluir o prontuário de {anamnese.paciente.nome} "
            f"porque existem {total_exames} exame(s) físico(s) vinculado(s). "
            "Exclua os exames primeiro ou desvincule-os."
        )
    else:
        # 4. Se estiver limpa, procede com a exclusão
        nome_paciente = anamnese.paciente.nome
        anamnese.delete()
        messages.success(request, f"O prontuário de {nome_paciente} foi excluído com sucesso.")

    return redirect('consulta_anamnese')


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


@login_required
def cadastro_exame_fisico(request, pk=None):
    if pk:
        # Edição de exame existente
        exame = get_object_or_404(ExameFisico, pk=pk)
        anamnese = exame.anamnese
    else:
        exame = None
        anamnese_id = request.GET.get('vinculo')

        if anamnese_id:
            # Fluxo tradicional: vindo de uma anamnese já aberta
            anamnese = get_object_or_404(Anamnese, id=anamnese_id)
        else:
            # NOVO FLUXO: Criar anamnese simplificada para novo exame avulso
            paciente_id = request.GET.get('paciente_id')
            paciente_obj = get_object_or_404(Paciente, id=paciente_id)

            # Criação da anamnese de suporte obrigatória pelo banco de dados
            anamnese = Anamnese.objects.create(
                paciente=paciente_obj,
                usuario=request.user,
                queixa_principal="Anamnese simplificada (vínculo automático para exame físico).",
                hma="Registro gerado automaticamente via tela de Gestão de Pacientes.",
                data_criacao=timezone.now()
            )

    paciente = anamnese.paciente  # Acessando o paciente vinculado

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

            # TRATAMENTO CORRETO DE DECIMAIS:
            # Capturamos o valor, limpamos espaços e verificamos se não é uma string vazia ou "None"
            def limpar_decimal(valor):
                if not valor or str(valor).strip().lower() == 'none' or str(valor).strip() == '':
                    return None
                return str(valor).replace(',', '.')

            exame.peso = limpar_decimal(request.POST.get('eg_peso'))
            exame.altura = request.POST.get('eg_altura') or None  # IntegerField geralmente aceita None direto
            exame.imc = limpar_decimal(request.POST.get('eg_imc'))
            exame.temperatura = limpar_decimal(request.POST.get('eg_temp'))

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

        # --- 3. SE FOR SINTOMA DOR ---
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
            exame.tipo_esfigmomanometro = request.POST.get('tipo_esfigmomanometro')
            exame.pa_sentado_sistolica = request.POST.get('pa_sentado_sistolica')
            exame.pa_sentado_diastolica = request.POST.get('pa_sentado_diastolica')
            exame.pa_deitado_sistolica = request.POST.get('pa_deitado_sistolica')
            exame.pa_deitado_diastolica = request.POST.get('pa_deitado_diastolica')
            exame.fc_deitado = request.POST.get('fc_deitado')
            exame.pa_em_pe_sistolica = request.POST.get('pa_em_pe_sistolica')
            exame.pa_em_pe_diastolica = request.POST.get('pa_em_pe_diastolica')
            exame.fc_em_pe = request.POST.get('fc_em_pe')

            # --- 5. SE FOR EXAME PSÍQUICO ---
        elif tipo == 'psiquico':
            exame.impressao_geral_psic = request.POST.get('impressao_geral_psic')
            exame.consciencia_psic = request.POST.get('consciencia_psic')
            exame.atencao_psic = request.POST.get('atencao_psic')
            exame.orientacao_psic = request.POST.get('orientacao_psic')
            exame.sensopercepcao_psic = request.POST.get('sensopercepcao_psic')
            exame.memoria_psic = request.POST.get('memoria_psic')
            exame.psicomotricidade_psic = request.POST.get('psicomotricidade_psic')
            exame.vontade_psic = request.POST.get('vontade_psic')
            exame.linguagem_psic = request.POST.get('linguagem_psic')
            exame.pensamento_psic = request.POST.get('pensamento_psic')
            exame.inteligencia_psic = request.POST.get('inteligencia_psic')
            exame.afetividade_humor_psic = request.POST.get('afetividade_humor_psic')


        # --- PARA OUTROS TIPOS / DESCRIÇÃO LIVRE ---
        else:
            exame.descricao_exame = request.POST.get('descricao_exame')

        exame.save()
        messages.success(request, f"Exame de {paciente.nome} salvo com sucesso!")
        return redirect('gerenciar_exames')

    return render(request, 'cadastro_exame_fisico.html', {
        'exame': exame,
        'anamnese': anamnese,
        'paciente': paciente,
        'tipos_opcoes': ExameFisico.TIPOS_EXAME
    })


def gerenciar_exames(request, anamnese_id=None):  # anamnese_id agora é opcional
    if anamnese_id:
        # Visualização de um paciente específico
        anamnese = get_object_or_404(Anamnese, id=anamnese_id)
        exames = anamnese.exames_fisicos.all()
    else:
        # Visualização GERAL vinda da Sidebar
        anamnese = None
        exames = ExameFisico.objects.filter(anamnese__usuario=request.user).order_by('-data_exame')

    return render(request, 'gerenciar_exames.html', {
        'anamnese': anamnese,
        'exames': exames,
        'modo_geral': anamnese is None  # Ajuda o template a saber se exibe o nome do paciente
    })


def excluir_exame_fisico(request, pk):
    exame = get_object_or_404(ExameFisico, pk=pk)
    anamnese_id = exame.anamnese.id
    exame.delete()

    messages.success(request, "Exame físico removido com sucesso!")
    return redirect('gerenciar_exames', anamnese_id=anamnese_id)


def render_to_pdf(template_src, context_dict={}):
    html_string = render_to_string(template_src, context_dict)
    html = HTML(string=html_string, base_url=None)  # base_url ajuda a encontrar imagens/css
    result = html.write_pdf()

    # Retorna o Response
    response = HttpResponse(result, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="relatorio.pdf"'
    return response


def gerar_pdf_anamnese(request, pk):
    anamnese = get_object_or_404(Anamnese, pk=pk)
    paciente = anamnese.paciente
    exames_vinculados = anamnese.exames_fisicos.all().order_by('-data_exame')

    # Lógica para calcular a idade
    idade = None
    if paciente.data_nascimento:
        hoje = date.today()
        nasc = paciente.data_nascimento
        # Subtrai os anos e ajusta se o aniversário ainda não ocorreu este ano
        idade = hoje.year - nasc.year - ((hoje.month, hoje.day) < (nasc.month, nasc.day))

    context = {
        'anamnese': anamnese,
        'paciente': paciente,
        'idade': idade,
        'exames': exames_vinculados,
        'data_impressao': timezone.now(),
        'usuario_nome': request.user.get_full_name() or request.user.username,  # Passa o nome aqui
    }
    return render_to_pdf('pdf_anamnese.html', context)


def gerar_pdf_exame_individual(request, exame_id):
    exame = get_object_or_404(ExameFisico, id=exame_id)
    context = {
        'anamnese': exame.anamnese,
        'exames': [exame],
        'data_impressao': timezone.now(),
        'usuario_nome': request.user.get_full_name() or request.user.username,  # Passa o nome aqui
    }
    return render_to_pdf('pdf_exames.html', context)


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


@login_required
def selecionar_paciente_exame(request):
    # Lista todos os pacientes (ou filtra conforme busca)
    pacientes = Paciente.objects.all().order_by('nome')

    nome_busca = request.GET.get('nome')
    if nome_busca:
        pacientes = pacientes.filter(nome__icontains=nome_busca)

    return render(request, 'selecionar_paciente_exame.html', {'pacientes': pacientes})


@login_required
def selecionar_paciente_anamnese(request):
    # Lista todos os pacientes (ou filtra conforme busca)
    pacientes = Paciente.objects.all().order_by('nome')

    nome_busca = request.GET.get('nome')
    if nome_busca:
        pacientes = pacientes.filter(nome__icontains=nome_busca)

    return render(request, 'selecionar_paciente_anamnese.html', {'pacientes': pacientes})


@login_required
@require_POST  # Garante que essa view só aceite requisições POST
def criar_anamnese_rapida(request):
    # 1. Coleta de dados do POST
    nome = request.POST.get('nome')
    cpf = request.POST.get('cpf')
    rg = request.POST.get('rg')

    # 2. Validação de Negócio: CPF ou RG obrigatórios
    if not cpf and not rg:
        return JsonResponse({
            'success': False,
            'errors': "É obrigatório informar o CPF ou o RG para cadastrar o paciente."
        }, status=400)

    try:
        # 3. Criação do Paciente
        novo_paciente = Paciente.objects.create(
            nome=nome,
            cpf=cpf or None,
            rg=rg or None,
            email=request.POST.get('email') or None,
            data_nascimento=request.POST.get('data_nascimento') or None,
            sexo=request.POST.get('sexo'),
            cor_etnia=request.POST.get('cor_etnia'),
            religiao=request.POST.get('religiao'),
            profissao=request.POST.get('profissao'),
            estado_civil=request.POST.get('estado_civil'),
            endereco=request.POST.get('endereco'),
            plano_saude=request.POST.get('plano_saude'),
            usuario=request.user
        )

        # 4. Criação da Anamnese automática (opcional, dependendo se você quer
        # que o clique em "Sim" abra uma anamnese em branco ou essa automática)
        Anamnese.objects.create(
            paciente=novo_paciente,
            usuario=request.user,
            queixa_principal="Paciente cadastrado via recepção/triagem."
        )

        # Retornamos o sucesso e o ID do paciente para o JavaScript
        return JsonResponse({
            'success': True,
            'paciente_id': novo_paciente.id,
            'mensagem': f"Paciente {nome} cadastrado com sucesso!"
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'errors': str(e)
        }, status=500)



User = get_user_model()  # Define a variável User para o seu modelo customizado


def iniciar_assinatura(request):
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    # Dados para criar a assinatura vinculada ao estudante
    subscription_data = {
        "preapproval_plan_id": "7fb4e37165a648bc8e9935f0779271d8",
        "reason": "Assinatura Mensal MedTools",
        "external_reference": str(request.user.id),
        "payer_email": request.user.email,
        "auto_recurring": {
            "frequency": 1,
            "frequency_type": "months",
            "transaction_amount": 5.50,
            "currency_id": "BRL"
        },
        "back_url": request.build_absolute_uri('/painel/'),
        "status": "pending"
    }

    subscription_response = sdk.preapproval().create(subscription_data)
    # Este link levará o médico para cadastrar o cartão e autorizar a recorrência
    init_point = subscription_response["response"]["init_point"]

    return render(request, 'vendas.html', {'init_point': init_point})


@login_required
def pagina_vendas(request):
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    # 1. LINK DE ASSINATURA (CARTÃO)
    plan_id = "7fb4e37165a648bc8e9935f0779271d8"
    init_point_assinatura = f"https://www.mercadopago.com.br/subscriptions/checkout?preapproval_plan_id={plan_id}&external_reference={request.user.id}"

    # 2. GERAÇÃO DO PIX DE R$ 1,00
    # GERAÇÃO DO PIX DE R$ 1,00 (Ajustado)
    preference_data = {
        "items": [
            {
                "id": "MEDTOOLS-001",
                "title": "Acesso MedTools - Teste Real",
                "quantity": 1,
                "unit_price": 1.00,
                "currency_id": "BRL",
            }
        ],
        "payer": {
            "email": request.user.email,
            # Se o seu modelo de usuário tiver CPF, envie aqui para agilizar o Pix
            # "identification": {"type": "CPF", "number": "00000000000"}
        },
        "external_reference": str(request.user.id),
        "payment_methods": {
            # Mantemos a exclusão para forçar o Pix
            "excluded_payment_types": [
                {"id": "credit_card"},
                {"id": "debit_card"},
                {"id": "ticket"}
            ],
            "installments": 1
        }
    }

    pix_res = sdk.preference().create(preference_data)

    # VERIFICAÇÃO DE ERRO
    if pix_res["status"] >= 400:
        print("❌ ERRO AO GERAR PIX EM PRODUÇÃO:", pix_res["response"])  # Olhe isso no terminal!
        init_point_pix = "#"
    else:
        init_point_pix = pix_res["response"].get("init_point")

    return render(request, 'vendas.html', {
        'init_point_assinatura': init_point_assinatura,
        'init_point_pix': init_point_pix
    })


# 2. VIEW DO WEBHOOK (PROCESSAMENTO AUTOMÁTICO)
@csrf_exempt
def webhook_mercado_pago(request):
    print(f"🔔 WEBHOOK RECEBIDO: {request.body}")  # Mostra o conteúdo bruto no terminal
    """Recebe notificações do Mercado Pago e ativa a licença do usuário."""

    # Tenta obter o ID do recurso enviado pelo Mercado Pago
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    resource_id = data.get('data', {}).get('id')
    action = data.get('action')

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    # Caso seja um pagamento (Pix)
    if action == "payment.created":
        payment_info = sdk.payment().get(resource_id)
        if payment_info["status"] == 200 and payment_info["response"]["status"] == "approved":
            user_id = payment_info["response"].get("external_reference")
            ativar_usuario(user_id)

    # Caso seja uma assinatura (Cartão)
    elif action in ["subscription_preapproval.created", "subscription_preapproval.updated"]:
        sub_info = sdk.preapproval().get(resource_id)
        if sub_info["status"] == 200 and sub_info["response"]["status"] == "authorized":
            user_id = sub_info["response"].get("external_reference")
            ativar_usuario(user_id)

    return HttpResponse(status=200)


def ativar_usuario(user_id):
    """Função auxiliar para atualizar o banco de dados."""
    if not user_id:
        return

    User = get_user_model()
    try:
        user = User.objects.get(id=user_id)
        user.licenca_ativa = True
        user.expiracao_licenca = timezone.now() + timedelta(days=30)
        user.save()
    except User.DoesNotExist:
        pass


@login_required
def estudo_flashcards(request):
    # 1. Captura a categoria selecionada via GET (filtro da tela)
    categoria_selecionada = request.GET.get('categoria')

    # 2. Base da Query: Cards do usuário OU públicos que venceram HOJE
    flashcards_query = Flashcard.objects.filter(
        Q(usuario=request.user) | Q(is_publico=True),
        proxima_revisao__lte=timezone.now()
    )

    # 3. Aplica o filtro de categoria se o usuário selecionou uma
    if categoria_selecionada:
        flashcards_query = flashcards_query.filter(categoria=categoria_selecionada)

    # 4. Ordenação e seleção do card atual (o primeiro da fila)
    card_atual = flashcards_query.order_by('proxima_revisao').first()

    # 5. Lista de todas as categorias disponíveis para preencher o select no HTML
    categorias = Flashcard.objects.filter(
        Q(usuario=request.user) | Q(is_publico=True)
    ).values_list('categoria', flat=True).distinct()

    return render(request, 'flashcards/estudo.html', {
        'card': card_atual,
        'categorias': categorias,
        'categoria_ativa': categoria_selecionada
    })


@login_required
def responder_flashcard(request, card_id):
    if request.method == "POST":
        card = get_object_or_404(Flashcard, id=card_id)
        qualidade = int(request.POST.get('qualidade'))  # 1: Difícil, 2: Médio, 3: Fácil

        # Lógica de Revisão Espaçada Simplificada
        if qualidade == 3:  # Fácil
            card.intervalo += 7
        elif qualidade == 2:  # Médio
            card.intervalo += 3
        else:  # Difícil
            card.intervalo = 1

        card.proxima_revisao = timezone.now() + timedelta(days=card.intervalo)
        card.save()

    return redirect('estudo_flashcards')


@login_required
def criar_flashcard(request):  # <-- Verifique se o nome é exatamente este
    if request.method == 'POST':
        form = FlashcardForm(request.POST, request.FILES)
        if form.is_valid():
            novo_card = form.save(commit=False)
            novo_card.usuario = request.user
            novo_card.save()
            return redirect('estudo_flashcards')
    else:
        form = FlashcardForm()

    return render(request, 'flashcards/criar.html', {'form': form})


@login_required
def dashboard_flashcards(request):
    # Filtros base
    meus_filtros = Q(usuario=request.user) | Q(is_publico=True)

    # Métricas para os "Cards de Resumo"
    total_cards = Flashcard.objects.filter(meus_filtros).count()

    revisoes_hoje = Flashcard.objects.filter(
        meus_filtros,
        proxima_revisao__lte=timezone.now()
    ).count()

    # Categorias para o usuário escolher por onde começar
    estatisticas_categorias = Flashcard.objects.filter(meus_filtros).values('categoria').annotate(
        total= Count('id'),
        pendentes= Count('id', filter=Q(proxima_revisao__lte=timezone.now()))
    ).order_by('-pendentes')

    context = {
        'total_cards': total_cards,
        'revisoes_hoje': revisoes_hoje,
        'categorias': estatisticas_categorias,
    }
    return render(request, 'flashcards/dashboard_especifico.html', context)


@login_required
def visualizacao_aula(request, aula_id):
    aula_atual = get_object_or_404(Aula, id=aula_id)
    modulos = Modulo.objects.prefetch_related('aulas').order_by('ordem')

    aulas_concluidas = ProgressoAula.objects.filter(
        usuario=request.user, concluida=True
    ).values_list('aula_id', flat=True)

    context = {
        'aula': aula_atual,
        'modulos': modulos,
        'aulas_concluidas': aulas_concluidas,
    }
    # Certifique-se de que a pasta é curso_semiologia
    return render(request, 'curso_semiologia/curso.html', context)


@login_required
def marcar_concluida(request, aula_id):
    aula = get_object_or_404(Aula, id=aula_id)
    ProgressoAula.objects.get_or_create(usuario=request.user, aula=aula, defaults={'concluida': True})
    return redirect('visualizacao_aula', aula_id=aula.id)


@login_required
def indice_curso(request):
    modulos = Modulo.objects.prefetch_related('aulas').order_by('ordem')

    # Lista de IDs de aulas concluídas pelo usuário
    aulas_concluidas = ProgressoAula.objects.filter(
        usuario=request.user, concluida=True
    ).values_list('aula_id', flat=True)

    # Primeira aula para o botão "Continuar"
    primeira_aula = Aula.objects.order_by('modulo__ordem', 'ordem').first()

    # Cálculo de progresso total
    total_aulas = Aula.objects.count()
    concluidas_count = len(aulas_concluidas)
    progresso_total = int((concluidas_count / total_aulas) * 100) if total_aulas > 0 else 0

    return render(request, 'curso_semiologia/indice.html', {
        'modulos': modulos,
        'aulas_concluidas': aulas_concluidas,
        'progresso_total': progresso_total,
        'primeira_aula': primeira_aula,
    })

# Rota temporária para evitar o erro NoReverseMatch até você criar o banco de questões
@login_required
def banco_questoes(request):
    return render(request, 'em_construcao.html')