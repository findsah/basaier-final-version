# Generated by Django 2.2.17 on 2021-04-13 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0051_auto_20210412_2337'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compaigncategory',
            name='country',
            field=models.CharField(choices=[('Philippines', 'Philippines'), ('Morocco', 'Morocco'), ('Niger', 'Niger'), ('India', 'India'), ('Yemen', 'Yemen'), ('Uganda', 'Uganda'), ('Benin', 'Benin'), ('Tanzania', 'Tanzania'), ('Sri Lanka', 'Sri Lanka'), ('Kenya', 'Kenya'), ('Gambia', 'Gambia'), ('Senegal', 'Senegal'), ('Pakistan', 'Pakistan'), ('Syria', 'Syria'), ('Sudan', 'Sudan'), ('Kuwait', 'Kuwait')], default='Kuwait', max_length=255),
        ),
    ]
