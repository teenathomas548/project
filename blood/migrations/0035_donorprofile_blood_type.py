# Generated by Django 5.1 on 2024-10-20 17:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blood', '0034_donorprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='donorprofile',
            name='blood_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='blood.bloodtype'),
        ),
    ]
