# Generated by Django 2.2.17 on 2021-03-22 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0043_donatesponsor_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='location',
            field=models.CharField(choices=[('Lebanon', 'Lebanon'), ('Tunisia', 'Tunisia'), ('India', 'India'), ('Somalia', 'Somalia'), ('Burkina Faso', 'Burkina Faso'), ('Kenya', 'Kenya'), ('Jordan', 'Jordan'), ('MONTENEGRO', 'MONTENEGRO'), ('Bosnia and Herzegovina', 'Bosnia and Herzegovina'), ('Palestine', 'Palestine'), ('Senegal', 'Senegal'), ('Albania', 'Albania'), ('Pakistan', 'Pakistan'), ('Ethiopia', 'Ethiopia'), ('Sudan', 'Sudan'), ('Kuwait', 'Kuwait')], default='Kuwait', max_length=255),
        ),
    ]
