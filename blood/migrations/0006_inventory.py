# Generated by Django 5.1 on 2024-10-01 16:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blood', '0005_bloodtype'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('inventory_id', models.AutoField(primary_key=True, serialize=False)),
                ('units_available', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('blood_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blood.bloodtype')),
            ],
        ),
    ]
