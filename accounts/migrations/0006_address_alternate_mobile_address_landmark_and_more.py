# Generated by Django 4.2.3 on 2023-08-23 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_profile_address_filled'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='alternate_mobile',
            field=models.CharField(max_length=15, null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='landmark',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='address',
            name='mobile',
            field=models.CharField(max_length=15, null=True),
        ),
    ]
