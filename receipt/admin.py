from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import NotaFiscal

@admin.register(NotaFiscal)
class NotaFiscalAdmin(admin.ModelAdmin):
    list_display = ('nf', 'data', 'turno', 'un_origem', 'qnt_pallet', 'tipo_veiculo', 'peso_nota')
    list_filter = ('turno', 'data')
    search_fields = ('nf', 'un_origem', 'tipo_veiculo')
