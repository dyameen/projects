# Generated by Django 3.2.15 on 2022-08-29 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_test', '0002_rename_new_users_users'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='users',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='users',
            name='timestamp',
        ),
    ]
