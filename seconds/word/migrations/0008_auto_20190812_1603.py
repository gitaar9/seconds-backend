# Generated by Django 2.0.13 on 2019-08-12 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('word', '0007_optionalenglishword'),
    ]

    operations = [
        migrations.AlterField(
            model_name='word',
            name='word',
            field=models.CharField(max_length=32),
        ),
        migrations.AlterUniqueTogether(
            name='word',
            unique_together={('word', 'language')},
        ),
    ]
