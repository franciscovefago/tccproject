# Generated by Django 4.2.2 on 2023-07-04 13:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gps_app', '0007_gpsdevice_cercado'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cercado',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lat1', models.DecimalField(decimal_places=3, max_digits=9)),
                ('lon1', models.DecimalField(decimal_places=3, max_digits=9)),
                ('lat2', models.DecimalField(decimal_places=3, max_digits=9)),
                ('lon2', models.DecimalField(decimal_places=3, max_digits=9)),
                ('lat3', models.DecimalField(decimal_places=3, max_digits=9)),
                ('lon3', models.DecimalField(decimal_places=3, max_digits=9)),
                ('lat4', models.DecimalField(decimal_places=3, max_digits=9)),
                ('lon4', models.DecimalField(decimal_places=3, max_digits=9)),
            ],
        ),
        migrations.AlterField(
            model_name='gpsdevice',
            name='cercado',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='gps_app.cercado'),
        ),
    ]