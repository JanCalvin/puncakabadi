# Generated by Django 4.2.5 on 2024-03-16 09:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abadi', '0005_rename_idbahanbaku_saldoawalbahanbaku_kodeproduk'),
    ]

    operations = [
        migrations.RenameField(
            model_name='saldoawalartikel',
            old_name='IDBahanBaku',
            new_name='KodeProduk',
        ),
    ]