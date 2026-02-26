from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario
from .models import Modulo, Aula, ProgressoAula


class UsuarioAdmin(UserAdmin):
    # Alterado de 'nome' para 'first_name' e 'last_name'
    list_display = ('email', 'first_name', 'last_name', 'email_validado', 'expiracao_licenca', 'is_staff')

    # Adicionamos seus campos personalizados (telefone, etc) nos formulários de edição
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('telefone', 'email_validado', 'expiracao_licenca')}),
    )

    # Campos para o formulário de criação de novo usuário via Admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('first_name', 'last_name', 'telefone', 'email_validado', 'expiracao_licenca')}),
    )


admin.site.register(Usuario, UsuarioAdmin)



@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ('ordem', 'titulo')
    ordering = ('ordem',)

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'modulo', 'ordem', 'categoria_relacionada')
    list_filter = ('modulo', 'categoria_relacionada')
    search_fields = ('titulo',)

admin.site.register(ProgressoAula)