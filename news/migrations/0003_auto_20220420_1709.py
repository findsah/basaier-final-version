# Generated by Django 2.2.17 on 2022-04-20 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_prnews_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='sciencenews',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='stories/videos/%Y/%m/%d'),
        ),
        migrations.AlterField(
            model_name='sciencenews',
            name='image',
            field=models.FileField(blank=True, null=True, upload_to='stories/%Y/%m/%d'),
        ),
    ]
