# Generated by Django 3.0 on 2022-01-21 19:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_auto_20220121_1516'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contributor',
            old_name='first_name',
            new_name='first_names',
        ),
        migrations.RenameField(
            model_name='contributor',
            old_name='last_name',
            new_name='last_names',
        ),
    ]