# Generated by Django 5.1 on 2024-10-25 06:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blood', '0039_doctor_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='hospital',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]