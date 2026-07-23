from django.conf import settings
from django.db import models


class RegistroMensal(models.Model):
    MESES = [
        (1, "Janeiro"),
        (2, "Fevereiro"),
        (3, "Março"),
        (4, "Abril"),
        (5, "Maio"),
        (6, "Junho"),
        (7, "Julho"),
        (8, "Agosto"),
        (9, "Setembro"),
        (10, "Outubro"),
        (11, "Novembro"),
        (12, "Dezembro"),
    ]

    NIVEL_CHOICES = [
        ("Crítico", "Crítico"),
        ("Moderado", "Moderado"),
        ("Suave", "Suave"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registros_financeiros",
    )
    mes = models.PositiveSmallIntegerField(choices=MESES)
    ano = models.PositiveIntegerField()
    salario = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_contas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_faturas = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_gastos_extras = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )
    total_bicos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    renda_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_gastos = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    recomendacao_guardar = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    nivel = models.CharField(max_length=20, choices=NIVEL_CHOICES, default="Suave")
    mensagem = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-ano", "-mes"]
        constraints = [
            models.UniqueConstraint(
                fields=["usuario", "mes", "ano"],
                name="registro_mensal_unico_por_usuario",
            )
        ]
        verbose_name = "Registro mensal"
        verbose_name_plural = "Registros mensais"

    def __str__(self):
        return f"{self.usuario} - {self.get_mes_display()}/{self.ano}"


class ItemFinanceiro(models.Model):
    TIPO_CONTA = "conta"
    TIPO_FATURA = "fatura"
    TIPO_GASTO = "gasto"
    TIPO_bico = "bico"

    TIPO_CHOICES = [
        (TIPO_CONTA, "Conta fixa"),
        (TIPO_FATURA, "Fatura"),
        (TIPO_GASTO, "Gasto extra"),
        (TIPO_bico, "Renda extra"),
    ]

    registro = models.ForeignKey(
        RegistroMensal,
        on_delete=models.CASCADE,
        related_name="itens",
    )
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    nome = models.CharField(max_length=120)
    valor = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["tipo", "nome"]
        verbose_name = "Item financeiro"
        verbose_name_plural = "Itens financeiros"

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nome}"
