# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-27 11:32
# from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Yaas', '0004_newauction_auctionban'),
    ]

    operations = [
        migrations.CreateModel(
            name='bidAuctionModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bidPrice', models.DecimalField(decimal_places=2, max_digits=6)),
                ('bidBiddersID', models.PositiveIntegerField(default=0)),
                ('bidCreateDate', models.DateTimeField(auto_now_add=True)),
                ('bidAuctionId', models.IntegerField(default=0)),
            ],
        ),
    ]