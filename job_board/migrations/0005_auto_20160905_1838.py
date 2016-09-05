# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-05 18:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_board', '0004_siteconfig_admin_email'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='category',
            managers=[
            ],
        ),
        migrations.AlterModelManagers(
            name='company',
            managers=[
            ],
        ),
        migrations.AlterModelManagers(
            name='job',
            managers=[
            ],
        ),
        migrations.AlterModelManagers(
            name='siteconfig',
            managers=[
            ],
        ),
        migrations.AddField(
            model_name='job',
            name='remote',
            field=models.BooleanField(default=False, help_text='Select if this job allows 100% remote working'),
            preserve_default=False,
        ),
    ]
