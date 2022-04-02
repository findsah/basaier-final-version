# Generated by Django 2.2.17 on 2022-04-02 17:52

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='createownprojectmodel',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='createownprojectmodel',
            name='generatedLink',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
