# Add phone to HistoricalUser to match the AddField in 0002_user_phone.
# simple_history does not auto-update the historical table when fields
# are added via plain AddField — it must be done manually.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicaluser',
            name='phone',
            field=models.CharField(
                blank=True,
                help_text='Número de telefone para notificações WhatsApp (ex: +2389991234)',
                max_length=20,
            ),
        ),
    ]
