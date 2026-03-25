from django.db import migrations, models


def blank_strings_to_null(apps, schema_editor):
    Empleado = apps.get_model("users", "Empleado")
    Empleado.objects.filter(numero_documento="").update(numero_documento=None)


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_empleado_codigo_qr"),
    ]

    operations = [
        migrations.AlterField(
            model_name="empleado",
            name="numero_documento",
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.RunPython(blank_strings_to_null, migrations.RunPython.noop),
    ]
