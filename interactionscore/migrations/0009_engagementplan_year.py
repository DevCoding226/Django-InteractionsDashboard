# Generated by Django 2.0.6 on 2018-07-02 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactionscore', '0008_remove_engagementplan_year'),
    ]

    operations = [
        migrations.AddField(
            model_name='engagementplan',
            name='year',
            field=models.IntegerField(default=2018),
            preserve_default=False,
        ),
    ]
