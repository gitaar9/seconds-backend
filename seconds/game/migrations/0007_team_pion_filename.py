# Generated by Django 3.2.18 on 2023-04-22 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0006_game_language'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='pion_filename',
            field=models.CharField(default='pion1.png', max_length=20),
        ),
    ]
