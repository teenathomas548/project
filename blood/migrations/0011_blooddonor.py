# Generated by Django 5.1 on 2024-10-04 17:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blood', '0010_rename_id_registration_user_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='BloodDonor',
            fields=[
                ('donor_id', models.AutoField(primary_key=True, serialize=False)),
                ('last_donation_date', models.DateField(blank=True, null=True)),
                ('eligibility_status', models.CharField(default='Eligible', max_length=50)),
                ('blood_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blood.bloodtype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='blood.registration')),
            ],
            options={
                'db_table': 'blood_donors',
            },
        ),
    ]
