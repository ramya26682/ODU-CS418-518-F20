# Generated by Django 2.1.1 on 2020-11-17 03:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dl_app', '0004_auto_20201116_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search_history',
            name='search',
            field=models.CharField(default='P-0001', max_length=500, null=True),
        ),
    ]
