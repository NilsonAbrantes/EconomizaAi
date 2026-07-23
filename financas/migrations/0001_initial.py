# Generated for the initial EconomizaAi database schema.

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="RegistroMensal",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "mes",
                    models.PositiveSmallIntegerField(
                        choices=[
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
                    ),
                ),
                ("ano", models.PositiveIntegerField()),
                (
                    "salario",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=12,
                    ),
                ),
                (
                    "total_contas",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=12,
                    ),
                ),
                (
                    "total_faturas",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=12,
                    ),
                ),
                (
                    "total_bicos",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=12,
                    ),
                ),
                (
                    "renda_total",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=12,
                    ),
                ),
                (
                    "total_gastos",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=12,
                    ),
                ),
                (
                    "saldo_final",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=12,
                    ),
                ),
                (
                    "recomendacao_guardar",
                    models.DecimalField(
                        decimal_places=2,
                        default=0,
                        max_digits=12,
                    ),
                ),
                (
                    "nivel",
                    models.CharField(
                        choices=[
                            ("Crítico", "Crítico"),
                            ("Moderado", "Moderado"),
                            ("Suave", "Suave"),
                        ],
                        default="Suave",
                        max_length=20,
                    ),
                ),
                ("mensagem", models.TextField(blank=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Registro mensal",
                "verbose_name_plural": "Registros mensais",
                "ordering": ["-ano", "-mes"],
                "unique_together": {("mes", "ano")},
            },
        ),
        migrations.CreateModel(
            name="ItemFinanceiro",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("conta", "Conta fixa"),
                            ("fatura", "Fatura"),
                            ("bico", "bico"),
                        ],
                        max_length=20,
                    ),
                ),
                ("nome", models.CharField(max_length=120)),
                (
                    "valor",
                    models.DecimalField(
                        decimal_places=2,
                        max_digits=12,
                    ),
                ),
                (
                    "registro",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="itens",
                        to="financas.registromensal",
                    ),
                ),
            ],
            options={
                "verbose_name": "Item financeiro",
                "verbose_name_plural": "Itens financeiros",
                "ordering": ["tipo", "nome"],
            },
        ),
    ]
