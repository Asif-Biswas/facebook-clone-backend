# Generated by Django 3.1.2 on 2020-12-15 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fb', '0004_auto_20201215_1044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='post',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]