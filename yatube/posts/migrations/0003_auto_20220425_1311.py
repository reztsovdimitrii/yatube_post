# Generated by Django 2.2.9 on 2022-04-25 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20220425_1002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(unique=True),
        ),
        migrations.AlterField(
            model_name='group',
            name='title',
            field=models.CharField(max_length=200),
        ),
    ]
