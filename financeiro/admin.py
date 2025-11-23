from django.contrib import admin
from .models import Categoria, RegistroFinanceiro

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo')

@admin.register(RegistroFinanceiro)
class RegistroFinanceiroAdmin(admin.ModelAdmin):
    list_display = ('data', 'tipo', 'valor', 'categoria', 'criado_por')
    list_filter = ('categoria__tipo', 'categoria', 'data')
