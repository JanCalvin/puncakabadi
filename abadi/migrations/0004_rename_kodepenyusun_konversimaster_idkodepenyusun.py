# Generated by Django 4.2.5 on 2024-03-13 12:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abadi', '0003_alter_detailkonversiproduksi_iddetailkonversiproduksi_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='konversimaster',
            old_name='KodePenyusun',
            new_name='IDKodePenyusun',
        ),
    ]
