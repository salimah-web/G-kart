# Generated by Django 3.2.6 on 2021-09-23 08:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_rename_order_order_order_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproduct',
            name='color',
        ),
        migrations.RemoveField(
            model_name='orderproduct',
            name='size',
        ),
    ]