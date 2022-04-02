# Generated by Django 2.2.17 on 2022-04-02 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0012_auto_20210410_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='joinChat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(blank=True, max_length=255)),
                ('whatsappPhone', models.CharField(blank=True, max_length=255)),
                ('contactChoice', models.BooleanField(choices=[(False, 'no'), (True, 'yes')], default=False)),
            ],
            options={
                'verbose_name': 'Join Chat',
                'verbose_name_plural': 'Join Chats',
            },
        ),
    ]
