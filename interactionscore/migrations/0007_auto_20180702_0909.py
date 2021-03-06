# Generated by Django 2.0.6 on 2018-07-02 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactionscore', '0006_auto_20180702_0907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='description',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='resource',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='resource',
            name='zinc_number_country',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='resource',
            name='zinc_number_global',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
