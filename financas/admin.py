from django.contrib import admin

from .models import ItemFinanceiro, RegistroMensal


class ItemFinanceiroInline(admin.TabularInline):
    model = ItemFinanceiro
    extra = 0


@admin.register(RegistroMensal)
class RegistroMensalAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "mes",
        "ano",
        "salario",
        "renda_total",
        "total_gastos_extras",
        "total_gastos",
        "saldo_final",
        "nivel",
        "atualizado_em",
    )
    list_filter = ("ano", "mes", "nivel", "usuario")
    search_fields = (
        "usuario__first_name",
        "usuario__email",
        "ano",
        "nivel",
    )
    autocomplete_fields = ("usuario",)
    inlines = [ItemFinanceiroInline]


@admin.register(ItemFinanceiro)
class ItemFinanceiroAdmin(admin.ModelAdmin):
    list_display = ("registro", "tipo", "nome", "valor")
    list_filter = ("tipo",)
    search_fields = (
        "nome",
        "registro__usuario__first_name",
        "registro__usuario__email",
    )
