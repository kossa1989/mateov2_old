# Generated by Django 2.2.1 on 2019-05-31 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0005_auto_20190530_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='analyses',
            name='case_group',
            field=models.CharField(default='kod_prod,kod_sw,nr_ks', max_length=200),
            preserve_default=False,
        ),
    ]
