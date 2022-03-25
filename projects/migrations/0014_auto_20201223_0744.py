# Generated by Django 2.0.3 on 2020-12-23 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0013_auto_20201221_0750'),
    ]

    operations = [
        migrations.AddField(
            model_name='sponsorshipprojects',
            name='defined_amount',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='sponsorshipprojects',
            name='is_closed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sponsorshipprojects',
            name='is_defined',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sponsorshipprojects',
            name='is_hidden',
            field=models.BooleanField(choices=[(False, 'no'), (True, 'yes')], default=False),
        ),
        migrations.AddField(
            model_name='sponsorshipprojects',
            name='suggestedDonation',
            field=models.DecimalField(decimal_places=3, default=1.0, max_digits=10),
        ),
        migrations.AddField(
            model_name='sponsorshipprojects',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True),
        ),
    ]
