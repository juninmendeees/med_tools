from django import forms
from django.core.mail.message import EmailMessage

from core.models import Flashcard


class ContatoForm(forms.Form):

    nome = forms.CharField(label='Nome', max_length=100)
    email = forms.EmailField(label='E-mail', max_length=100)
    assunto = forms.CharField(label='Assunto')
    mensagem = forms.CharField(label='Mensagem', widget=forms.Textarea)

    def send_email(self):
        nome = self.cleaned_data['nome']
        email = self.cleaned_data['email']
        assunto = self.cleaned_data['assunto']
        mensagem = self.cleaned_data['mensagem']

        conteudo = f'Nome: {nome}\nE-mail: {email}\nAssunto: {assunto}\nMensagem: {mensagem}'

        email = EmailMessage(
            subject= 'Email enviado via formulario MedTools',
            body= conteudo,
            from_email= 'contato@medtools.com.br',
            headers= {'Reply-To': email},
        )
        email.send()


class FlashcardForm(forms.ModelForm):
    class Meta:
        model = Flashcard
        # Campos que aparecerão no formulário de criação
        fields = ['pergunta', 'resposta', 'categoria', 'imagem']

        # Estilização usando classes do Bootstrap
        widgets = {
            'pergunta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'resposta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'categoria': forms.TextInput(attrs={'class': 'form-control'}),
            'imagem': forms.FileInput(attrs={'class': 'form-control-file'}),
        }
