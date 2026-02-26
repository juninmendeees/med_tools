from django.utils import timezone
from core.models import Usuario


def verificar_expiracoes():
    agora = timezone.now()
    usuarios_expirados = Usuario.objects.filter(
        licenca_ativa=True, 
        expiracao_licenca__lt=agora
    )
    total = usuarios_expirados.update(licenca_ativa=False)
    return f"{total} usuários tiveram a licença desativada por expiração."