# Generated by Django 5.1.4 on 2025-01-14 19:01

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pairs', '0002_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('Z2', 'Z2'), ('Z2_LOW', 'Z2_LOW')], max_length=255)),
                ('date', models.DateField(default=datetime.datetime.now)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('pair', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='notifications', to='pairs.pair', to_field='name')),
            ],
        ),
    ]
