# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-04 12:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20170204_1329'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='issue',
            name='type',
        ),
    ]