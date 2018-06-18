# Generated by Django 2.0.6 on 2018-06-18 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactionscore', '0004_auto_20180618_0931'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='engagementplan',
            options={'permissions': (('approve_ep', 'Can approve engagement plans'), ('change_own_current_ep', 'Can change own current engagement plan'))},
        ),
        migrations.AlterField(
            model_name='user',
            name='affiliate_groups',
            field=models.ManyToManyField(null=True, related_name='users', to='interactionscore.AffiliateGroup'),
        ),
    ]
