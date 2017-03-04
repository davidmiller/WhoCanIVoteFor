# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-04 13:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elections', '0011_auto_20170303_1823'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostElection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('election', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elections.Election')),
            ],
        ),
        migrations.AddField(
            model_name='postelection',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='elections.Post'),
        ),
    ]
