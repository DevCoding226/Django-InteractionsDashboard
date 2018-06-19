# Generated by Django 2.0.6 on 2018-06-18 15:45

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactionscore', '0009_auto_20180618_1304'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='engagementplan',
            options={'permissions': [('list_all_ep', 'Can list all EPs'), ('list_own_ag_ep', 'Can list EPs of own AGs'), ('change_own_current_ep', 'Can change own current EP'), ('approve_all_ep', 'Can approve all EPs'), ('approve_own_ag_ep', 'Can approve EPs of own AGs')]},
        ),
        migrations.AlterField(
            model_name='engagementplan',
            name='year',
            field=models.DateField(blank=True, default=datetime.datetime.today),
        ),
    ]