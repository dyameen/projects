# Generated by Django 3.2.15 on 2022-09-20 08:41

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('att_sys', '0009_alter_attendance_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attendance',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2022, 9, 20, 8, 41, 44, 245642, tzinfo=utc)),
        ),
    ]