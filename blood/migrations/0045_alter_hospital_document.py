# Generated by Django 5.1 on 2024-10-26 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blood', '0044_hospital_document'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hospital',
            name='document',
            field=models.FileField(blank=True, null=True, upload_to='document/'),
        ),
    ]
