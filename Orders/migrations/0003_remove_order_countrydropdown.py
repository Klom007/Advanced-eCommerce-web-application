# Generated by Django 5.0.4 on 2024-04-10 22:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Orders', '0002_rename_phonee_order_phone'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='countryDropDown',
        ),
    ]