# Generated by Django 3.2.13 on 2022-07-27 14:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shceduleremail', '0010_alter_detailtransaksi_options'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='detailtransaksi',
            table='report_transaksi',
        ),
    ]