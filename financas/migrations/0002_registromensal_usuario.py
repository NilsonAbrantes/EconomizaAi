from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def atribuir_registros_antigos(apps, schema_editor):
    RegistroMensal = apps.get_model("financas", "RegistroMensal")

    if not RegistroMensal.objects.filter(usuario__isnull=True).exists():
        return

    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)

    usuario_legado, _ = User.objects.get_or_create(
        username="__economiza_dados_anteriores__",
        defaults={
            "first_name": "Dados anteriores",
            "email": "dados-anteriores@economiza.local",
            "password": "!",
            "is_active": False,
        },
    )

    User.objects.filter(pk=usuario_legado.pk).update(
        password="!",
        is_active=False,
    )

    RegistroMensal.objects.filter(usuario__isnull=True).update(
        usuario_id=usuario_legado.pk
    )


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("financas", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="registromensal",
            name="usuario",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registros_financeiros",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(
            atribuir_registros_antigos,
            migrations.RunPython.noop,
        ),
        migrations.AlterUniqueTogether(
            name="registromensal",
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name="registromensal",
            name="usuario",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="registros_financeiros",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="registromensal",
            constraint=models.UniqueConstraint(
                fields=("usuario", "mes", "ano"),
                name="registro_mensal_unico_por_usuario",
            ),
        ),
    ]
