# Generated by Django 2.0.13 on 2019-07-22 10:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import seconds.game.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(default=seconds.game.models.random_string, max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='PlayerInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_query_name='teams', to='game.Game')),
            ],
        ),
        migrations.AddField(
            model_name='playerinfo',
            name='team',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_query_name='players', to='game.Team'),
        ),
        migrations.AddField(
            model_name='playerinfo',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
