# Generated by Django 4.2.2 on 2023-07-04 11:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gps_app', '0003_alter_gpsdevice_cercado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gpsdevice',
            name='last_updated',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 4, 11, 55, 47, 892202, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='previouslocation',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2023, 7, 4, 11, 55, 47, 892709, tzinfo=datetime.timezone.utc)),
        ),
    ]
