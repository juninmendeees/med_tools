from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

from django.contrib.auth.models import AbstractUser, BaseUserManager


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório')
        email = self.normalize_email(email)
        # Se o username não for passado, usamos o email
        extra_fields.setdefault('username', email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Garante que o username seja o email no superuser também
        extra_fields.setdefault('username', email)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    telefone = models.CharField(max_length=20)
    email_validado = models.BooleanField(default=False)
    expiracao_licenca = models.DateField(null=True, blank=True)
    licenca_ativa = models.BooleanField(default=False)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    # Vincula o Manager customizado
    objects = UsuarioManager()

    def tem_licenca_ativa(self):
        if self.licenca_ativa and self.expiracao_licenca:
            return self.expiracao_licenca > timezone.now()
        return False

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Paciente(models.Model):
    # Identidade do Paciente (Dados que não mudam a cada consulta)
    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, unique=True, null=True, blank=True)
    rg = models.CharField(max_length=20, unique=True, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    data_nascimento = models.DateField(null=True, blank=True)
    sexo = models.CharField(max_length=20, choices=[('M', 'Masculino'), ('F', 'Feminino')], null=True)
    cor_etnia = models.CharField(max_length=50, null=True, blank=True)
    religiao = models.CharField(max_length=100, null=True, blank=True)
    profissao = models.CharField(max_length=100, null=True, blank=True)
    estado_civil = models.CharField(max_length=50, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    plano_saude = models.CharField(max_length=100, null=True, blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome



class Anamnese(models.Model):
    # Relacionamento com o Usuário (Médico/Estudante)
    # Nota: User não é deletado, apenas inativado via is_active no Django
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    data_criacao = models.DateTimeField(auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(auto_now=True)

    # Relacionamento: Toda anamnese pertence a um paciente
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='anamneses')

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
        ('psiquico', 'Exame Psíquico'),
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

    # Campos para Exame Psíquico
    impressao_geral_psic = models.TextField(null=True, blank=True)
    consciencia_psic = models.TextField(null=True, blank=True)
    atencao_psic = models.TextField(null=True, blank=True)
    orientacao_psic = models.TextField(null=True, blank=True)
    sensopercepcao_psic = models.TextField(null=True, blank=True)
    memoria_psic = models.TextField(null=True, blank=True)
    psicomotricidade_psic = models.TextField(null=True, blank=True)
    vontade_psic = models.TextField(null=True, blank=True)
    linguagem_psic = models.TextField(null=True, blank=True)
    pensamento_psic = models.TextField(null=True, blank=True)
    inteligencia_psic = models.TextField(null=True, blank=True)
    afetividade_humor_psic = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.get_tipo_exame_display()} - {self.anamnese.nome}"



@receiver(pre_save, sender=Usuario)
def replicar_email_no_username(sender, instance, **kwargs):
    # Garante que sempre que o email mudar (ou for criado), o username acompanhe
    if instance.email:
        instance.username = instance.email


import uuid
import os
from django.db import models
from django.conf import settings
from django.utils import timezone


def get_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('flashcards/imagens/', filename)


class Flashcard(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    pergunta = models.TextField()
    resposta = models.TextField()
    imagem = models.ImageField(upload_to=get_file_path, null=True, blank=True)
    categoria = models.CharField(max_length=100)
    is_publico = models.BooleanField(default=False)

    # Lógica Estilo Anki (Algoritmo SM-2 simplificado)
    intervalo = models.IntegerField(default=0)  # Dias para a próxima revisão
    facilidade = models.FloatField(default=2.5)  # Fator de facilidade
    repeticoes = models.IntegerField(default=0)  # Quantas vezes foi acertado
    proxima_revisao = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.categoria} - {self.pergunta[:30]}"

class Modulo(models.Model):
        titulo = models.CharField(max_length=200)
        ordem = models.IntegerField(default=1)

        def __str__(self):
            return f"{self.ordem}. {self.titulo}"

class Aula(models.Model):
        modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='aulas')
        titulo = models.CharField(max_length=200)
        video_url = models.CharField(max_length=255, help_text="ID do vídeo ou URL (YouTube/Vimeo)")
        ordem = models.IntegerField(default=1)

        # Campos para filtros automáticos que você solicitou
        categoria_relacionada = models.CharField(max_length=100, help_text="Ex: Semiologia Cardiovascular")
        glossario_json = models.JSONField(default=dict, blank=True, help_text="Termos e definições da aula")

        def __str__(self):
            return self.titulo

class ProgressoAula(models.Model):
        usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
        aula = models.ForeignKey(Aula, on_delete=models.CASCADE)
        concluida = models.BooleanField(default=False)
        data_conclusao = models.DateTimeField(auto_now=True)

        class Meta:
            unique_together = ('usuario', 'aula')