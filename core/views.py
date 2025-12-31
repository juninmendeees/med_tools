from django.shortcuts import render

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

