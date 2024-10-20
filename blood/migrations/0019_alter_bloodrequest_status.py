# Generated by Django 5.1 on 2024-10-18 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blood', '0018_appointment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bloodrequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], max_length=10),
        ),
    ]