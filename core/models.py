from django.db import models
from django.contrib.auth.models import User

class Usuario(models.Model):
    usuario = models.CharField(max_length=100)
    senha = models.CharField(max_length=100)
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.IntegerField()
    def __str__(self):
        return self.nome

class Anamnese(models.Model):
    # Relacionamento com o Usuário (Médico/Estudante)
    # Nota: User não é deletado, apenas inativado via is_active no Django
    usuario = models.ForeignKey(User, on_delete=models.PROTECT, related_name='anamneses')
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    # --- 1. IDENTIFICAÇÃO ---
    nome = models.CharField(max_length=255)
    idade = models.PositiveIntegerField(null=True, blank=True)
    estado_civil = models.CharField(max_length=50, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    religiao = models.CharField(max_length=100, null=True, blank=True)
    etnia = models.CharField(max_length=50, null=True, blank=True)
    profissao = models.CharField(max_length=100, null=True, blank=True)
    plano_saude = models.CharField(max_length=100, null=True, blank=True)

    # --- 2. QUEIXA E HDA ---
    queixa_principal = models.TextField(null=True, blank=True)
    hma = models.TextField(null=True, blank=True) # História da Doença Atual

    # --- 3. INTERROGATÓRIO SISTEMÁTICO (IS) ---
    is_geral = models.TextField(null=True, blank=True)
    is_respiratorio = models.TextField(null=True, blank=True)
    is_cardiovascular = models.TextField(null=True, blank=True)
    is_digestorio = models.TextField(null=True, blank=True)

    # --- 4. ANTECEDENTES FISIOLÓGICOS ---
    gestacao_nascimento = models.TextField(null=True, blank=True)
    desenvolvimento_neural = models.TextField(null=True, blank=True)
    puberdade = models.CharField(max_length=50, null=True, blank=True)
    # Campos de desenvolvimento sexual capturados via input-group
    menarca_idade = models.CharField(max_length=10, null=True, blank=True)
    menopausa_idade = models.CharField(max_length=10, null=True, blank=True)
    sexarca_idade = models.CharField(max_length=10, null=True, blank=True)
    orientacao_sexual = models.CharField(max_length=100, null=True, blank=True)

    # --- 4. ANTECEDENTES PATOLÓGICOS ---
    doencas_infancia = models.CharField(max_length=255, null=True, blank=True)
    traumas = models.CharField(max_length=255, null=True, blank=True)
    alergias = models.CharField(max_length=255, null=True, blank=True)
    doencas_cronicas = models.TextField(null=True, blank=True)
    cirurgias_transfusoes = models.TextField(null=True, blank=True)
    medicamentos = models.TextField(null=True, blank=True)

    # --- 4. HISTÓRIA OBSTÉTRICA E FAMILIAR ---
    gesta = models.CharField(max_length=10, null=True, blank=True)
    para = models.CharField(max_length=10, null=True, blank=True)
    aborto = models.CharField(max_length=10, null=True, blank=True)
    vacinas = models.CharField(max_length=255, null=True, blank=True)
    antecedentes_familiares = models.TextField(null=True, blank=True)

    # --- 5. HÁBITOS E CONDIÇÕES DE VIDA ---
    alimentacao_peso = models.TextField(null=True, blank=True)
    atividades_fisicas = models.TextField(null=True, blank=True)
    ocupacoes = models.TextField(null=True, blank=True)
    viagens = models.TextField(null=True, blank=True)
    atividade_sexual = models.TextField(null=True, blank=True)
    tabaco = models.TextField(null=True, blank=True)
    alcool = models.TextField(null=True, blank=True)
    outras_drogas = models.TextField(null=True, blank=True)
    moradia_saneamento = models.TextField(null=True, blank=True)
    condicoes_economicas = models.TextField(null=True, blank=True)
    ajustamento_familiar = models.TextField(null=True, blank=True)
    contato_doentes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.nome} - {self.data_criacao.strftime('%d/%m/%Y')}"


class ExameFisico(models.Model):
    TIPOS_EXAME = [
        ('geral', 'Exame Físico Geral'),
        ('psiquico', 'Psíquico'),
        ('geriatria', 'Idoso / Geriatria Ampla'),
        ('pele', 'Pele'),
        ('linfonodos', 'Linfonodos'),
        ('pulsos', 'Pulsos'),
        ('pa', 'Pressão Arterial'),
        ('dor', 'Sintoma Dor'),
        ('nutricional', 'Nutricional'),
    ]

    # Opções para campos fechados (Porto)
    OPCAO_AUSENTE_PRESENTE = [('ausentes', 'Ausentes'), ('presentes', 'Presentes')]
    OPCAO_HIDRATACAO = [('hidratado', 'Hidratado'), ('desidratado', 'Desidratado')]
    OPCAO_MUCOSAS = [('coradas', 'Coradas'), ('hipocoradas', 'Hipocoradas'), ('hipercoradas', 'Hipercoradas')]
    OPCAO_DESENVOLVIMENTO = [('normal', 'Normal'), ('nanismo', 'Nanismo'), ('gigantismo', 'Gigantismo')]
    OPCAO_NUTRICAO = [('nutrido', 'Nutrido'), ('desnutrido', 'Desnutrido')]

    anamnese = models.ForeignKey('Anamnese', on_delete=models.CASCADE, related_name='exames_fisicos')
    tipo_exame = models.CharField(max_length=20, choices=TIPOS_EXAME, default='geral')
    data_exame = models.DateTimeField(auto_now_add=True)

    # --- Ectoscopia Inicial ---
    estado_geral = models.CharField(max_length=10, blank=True, null=True)
    facies = models.CharField(max_length=100, blank=True, null=True)
    nivel_consciencia = models.CharField(max_length=100, blank=True, null=True)

    # --- Pele, Mucosas e Hidratação ---
    hidratacao = models.CharField(max_length=20, choices=OPCAO_HIDRATACAO, blank=True, null=True)
    mucosas = models.CharField(max_length=20, choices=OPCAO_MUCOSAS, blank=True, null=True)
    respiracao = models.CharField(max_length=100, blank=True, null=True)
    pele_anexos = models.TextField(blank=True, null=True)

    # --- Novos Campos Solicitados ---
    movimentos_involuntarios = models.CharField(max_length=20, choices=OPCAO_AUSENTE_PRESENTE, blank=True, null=True)
    musculatura = models.TextField(blank=True, null=True)  # Placeholder: tônus e trofismo
    desenvolvimento_fisico = models.CharField(max_length=20, choices=OPCAO_DESENVOLVIMENTO, blank=True, null=True)
    estado_nutricional = models.CharField(max_length=20, choices=OPCAO_NUTRICAO, blank=True, null=True)
    veias_superficiais = models.CharField(max_length=20, choices=OPCAO_AUSENTE_PRESENTE, blank=True, null=True)
    veias_obs = models.CharField(max_length=255, blank=True, null=True)  # Placeholder: varizes e simetria
    circulacao_colateral = models.CharField(max_length=20, choices=[('ausente', 'Ausente'), ('presente', 'Presente')],
                                            blank=True, null=True)
    edema = models.TextField(blank=True, null=True)  # Placeholder: local, intensidade, etc.
    fala_linguagem = models.TextField(blank=True, null=True)
    marcha = models.CharField(max_length=255, blank=True, null=True)

    # --- Antropometria ---
    peso = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    altura = models.IntegerField(blank=True, null=True)
    imc = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)

    # --- Gerais ---
    atitude = models.CharField(max_length=100, blank=True, null=True)
    postura = models.CharField(max_length=100, blank=True, null=True)
    biotipo = models.CharField(max_length=50, blank=True, null=True)
    descricao_exame = models.TextField(blank=True, null=True)

    # --- HISTÓRIA NUTRICIONAL ---
    peso_habitual = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    perdeu_peso_6_meses = models.CharField(max_length=3, choices=[('sim', 'Sim'), ('nao', 'Não')], blank=True,
                                           null=True)
    quantidade_perdida_kg = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    percentual_perda = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    alteracao_peso_2_semanas = models.CharField(max_length=20,
                                                choices=[('aumento', 'Aumento'), ('sem_alteracao', 'Sem alteração'),
                                                         ('diminuicao', 'Diminuição')], blank=True, null=True)
    ingestao_alimentar = models.CharField(max_length=20, choices=[('sem_alteracao', 'Sem alterações'),
                                                                  ('com_alteracao', 'Com alterações')], blank=True,
                                          null=True)
    dieta_tipo = models.CharField(max_length=50,
                                  choices=[('solida', 'Sólida subótima'), ('liquida_completa', 'Líquida completa'),
                                           ('liquidos_hiper', 'Líquidos hipercalóricos'), ('inanicao', 'Inanição')],
                                  blank=True, null=True)

    # --- SINTOMAS GASTRINTESTINAIS (> 15 dias) ---
    sintomas_gi = models.CharField(max_length=100, blank=True,
                                   null=True)

    # --- CAPACIDADE FUNCIONAL E DOENÇA ---
    capacidade_funcional = models.CharField(max_length=50, choices=[('sem_alteracao', 'Sem alterações'),
                                                                    ('com_alteracao', 'Com alterações (disfunção)')],
                                            blank=True, null=True)
    tipo_disfuncao = models.CharField(max_length=50, choices=[('trabalho_subotima', 'Trabalho subótimo'),
                                                              ('ambulatorial', 'Em tratamento ambulatorial'),
                                                              ('acamado', 'Acamado')], blank=True, null=True)
    demanda_metabolica = models.CharField(max_length=20, choices=[('baixo', 'Baixo'), ('moderado', 'Moderado'),
                                                                  ('elevado', 'Elevado')], blank=True, null=True)

    # --- EXAME FÍSICO NUTRICIONAL (0=normal a 3=importante) ---
    perda_gordura_subcutanea = models.IntegerField(default=0, blank=True, null=True)
    perda_muscular = models.IntegerField(default=0, blank=True, null=True)
    ascite = models.IntegerField(default=0, blank=True, null=True)
    edema_sacral_nutri = models.IntegerField(default=0, blank=True, null=True)
    edema_tornozelo_nutri = models.IntegerField(default=0, blank=True, null=True)

    # --- AVALIAÇÃO SUBJETIVA FINAL ---
    classificacao_nutricional = models.CharField(max_length=30, choices=[('nutrido', 'Nutrido'),
                                                                         ('moderado', 'Moderadamente desnutrido'),
                                                                         ('grave', 'Gravemente desnutrido')],
                                                 blank=True, null=True)

    # --- CARACTERIZAÇÃO DA DOR ---
    localizacao_dor = models.CharField(max_length=255, blank=True, null=True)
    intensidade_dor = models.IntegerField(
        choices=[(i, str(i)) for i in range(11)],
        help_text="Escala de 0 (sem dor) a 10 (pior dor)",
        blank=True, null=True
    )
    qualidade_carater = models.CharField(
        max_length=50,
        choices=[
            ('queimacao', 'Queimação'), ('pontada', 'Pontada/Fisgada'),
            ('pulsatil', 'Pulsátil'), ('oprssiva', 'Opressiva'),
            ('colica', 'Cólica'), ('surda', 'Surda')
        ],
        blank=True, null=True
    )
    duracao_dor = models.CharField(max_length=100, blank=True, null=True)
    frequencia_dor = models.CharField(
        max_length=50,
        choices=[('continua', 'Contínua'), ('intermitente', 'Intermitente')],
        blank=True, null=True
    )
    fatores_agravantes = models.TextField(blank=True, null=True)
    fatores_atenuantes = models.TextField(blank=True, null=True)
    irradiacao_dor = models.CharField(max_length=255, blank=True, null=True)
    sintomas_associados_dor = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.get_tipo_exame_display()} - {self.anamnese.nome}"