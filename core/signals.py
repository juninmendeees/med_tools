from allauth.account.signals import email_confirmed
from django.dispatch import receiver
from .models import Usuario

@receiver(email_confirmed)
def marcar_email_como_validado(request, email_address, **kwargs):
    # Localiza o usuário dono do e-mail confirmado
    usuario = Usuario.objects.get(email=email_address.email)
    usuario.email_validado = True
    usuario.save()