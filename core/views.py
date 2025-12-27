from django.shortcuts import render
from .models import Produto

def index (request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def produto (request):
    produtos = Produto.objects.all()
    context = {
        'produtos': produtos
    }
    return render(request, 'produto.html', context)
