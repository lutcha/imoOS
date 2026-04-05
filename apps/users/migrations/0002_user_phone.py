# Generated manually for User phone field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(
                blank=True,
                help_text='Número de telefone para notificações WhatsApp (ex: +2389991234)',
                max_length=20
            ),
        ),
    ]
