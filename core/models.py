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
    # Relacionamento N:1 (Vários exames para uma anamnese)
    # Atende ao Requisito 3: Anamnese só deleta se não houver exames aqui
    anamnese = models.ForeignKey(Anamnese, on_delete=models.CASCADE, related_name='exames_fisicos')
    data_exame = models.DateTimeField(auto_now_add=True)
    descricao_exame = models.TextField() # Exemplo de campo, você poderá expandir depois

    def __str__(self):
        return f"Exame de {self.anamnese.nome} em {self.data_exame.strftime('%d/%m/%Y')}"