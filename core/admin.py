from django.contrib import admin


from .models import Produto, Cliente

class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'preco', 'quantidade')

class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'sobrenome', 'email', 'telefone')

admin.site.register(Produto, ProdutoAdmin)
admin.site.register(Cliente, ClienteAdmin)