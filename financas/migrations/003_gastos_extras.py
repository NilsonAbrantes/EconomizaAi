from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("financas", "0002_registromensal_usuario"),
    ]

    operations = [
        migrations.AddField(
            model_name="registromensal",
            name="total_gastos_extras",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=12,
            ),
        ),
        migrations.AlterField(
            model_name="itemfinanceiro",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("conta", "Conta fixa"),
                    ("fatura", "Fatura"),
                    ("gasto", "Gasto extra"),
                    ("bico", "Renda extra"),
                ],
                max_length=20,
            ),
        ),
    ]
