# Generated by Django 5.1 on 2024-10-21 15:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blood', '0036_delete_appointment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('appointment_date', models.DateField()),
                ('appointment_time', models.TimeField()),
                ('status', models.CharField(default='Scheduled', max_length=20)),
                ('donor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blood.donorprofile')),
            ],
            options={
                'db_table': 'appointments',
            },
        ),
    ]
