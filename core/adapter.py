from allauth.account.adapter import DefaultAccountAdapter

"""
Arquivo principal para a lógica de salvamento de usuários.
"""
class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        # Chama o salvamento padrão do Allauth
        user = super().save_user(request, user, form, commit=False)

        # Coleta os dados diretamente do POST do formulário HTML
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.telefone = request.POST.get('telefone', '')

        if commit:
            user.save()
        return user