# Generated by Django 3.2.15 on 2022-09-02 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('day10', '0002_movie_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movie',
            name='rating',
        ),
        migrations.AddField(
            model_name='movie',
            name='seat',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
    ]
