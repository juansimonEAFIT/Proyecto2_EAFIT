from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="empleado",
            name="codigo_qr",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
