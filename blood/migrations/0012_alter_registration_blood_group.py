# Generated by Django 5.1 on 2024-10-05 05:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blood', '0011_blooddonor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='blood_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blood.bloodtype'),
        ),
    ]
