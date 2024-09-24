# Generated by Django 5.1 on 2024-09-23 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blood', '0002_admin'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('campaign_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('location', models.CharField(max_length=255)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AlterModelTable(
            name='admin',
            table='blood_admin',
        ),
        migrations.AlterModelTable(
            name='registration',
            table='registrations',
        ),
    ]
