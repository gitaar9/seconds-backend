# Generated by Django 2.0.13 on 2019-08-12 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('word', '0006_auto_20190810_1231'),
    ]

    operations = [
        migrations.CreateModel(
            name='OptionalEnglishWord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=32, unique=True)),
            ],
        ),
    ]