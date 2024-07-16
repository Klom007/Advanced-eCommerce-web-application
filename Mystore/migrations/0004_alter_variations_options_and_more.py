# Generated by Django 5.0.4 on 2024-04-07 19:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Mystore', '0003_variations'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='variations',
            options={'verbose_name': 'Variation', 'verbose_name_plural': 'Variations'},
        ),
        migrations.AlterField(
            model_name='variations',
            name='variation_category',
            field=models.CharField(choices=[('color', 'color'), ('size', 'size')], max_length=100),
        ),
    ]
