# Generated by Django 4.0.6 on 2023-06-19 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('space', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentrecord',
            name='is_delete',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='rent',
            name='is_useful',
            field=models.BooleanField(default=True),
        ),
    ]
