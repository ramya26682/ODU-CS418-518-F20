# Generated by Django 2.2.1 on 2020-12-08 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dl_app', '0008_auto_20201208_1231'),
    ]

    operations = [
        migrations.CreateModel(
            name='likebutton2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, default='', max_length=500)),
                ('like', models.CharField(default='P-0001', max_length=500, null=True)),
            ],
        ),
    ]
