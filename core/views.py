from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContatoForm

def index (request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def cadastro(request):
    return render(request, 'cadastro.html')

def login(request):
    return render(request, 'login.html')

def cadastro_anamnese(request):
    return render(request, 'cadastro_anamnese.html')

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

