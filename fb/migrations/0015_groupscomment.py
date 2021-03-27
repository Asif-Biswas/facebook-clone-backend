# Generated by Django 3.1.2 on 2021-02-26 15:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fb', '0014_auto_20210224_1346'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupsComment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('body', models.TextField(max_length=1000)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fb.groupspost')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
    ]