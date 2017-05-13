# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-13 20:46
from __future__ import unicode_literals

import batches.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Batch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('batch_no', models.IntegerField(default=batches.models.Batch.next_batch_no, editable=False)),
                ('create_time', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('volume', models.DecimalField(decimal_places=1, max_digits=3)),
                ('deliv_addr_1', models.CharField(blank=True, max_length=50)),
                ('deliv_addr_2', models.CharField(blank=True, max_length=50)),
                ('deliv_addr_3', models.CharField(blank=True, max_length=50)),
                ('deliv_addr_4', models.CharField(blank=True, max_length=50)),
                ('eircode', models.CharField(blank=True, max_length=7)),
                ('notes', models.CharField(blank=True, max_length=200)),
                ('status', models.CharField(choices=[('PEND', 'Pending'), ('STAR', 'Started'), ('COMP', 'Completed'), ('ABOR', 'Aborted')], default='PEND', max_length=4)),
                ('ticket_created', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Drop',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drop_no', models.IntegerField()),
                ('no_in_batch', models.IntegerField()),
                ('volume', models.DecimalField(decimal_places=1, max_digits=3)),
                ('start_datetime', models.DateTimeField()),
                ('end_datetime', models.DateTimeField()),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='batches.Batch')),
            ],
        ),
        migrations.CreateModel(
            name='Drop_Detail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('design', models.IntegerField()),
                ('target', models.IntegerField()),
                ('actual', models.IntegerField()),
                ('moisture', models.IntegerField()),
                ('drop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='batches.Drop')),
            ],
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('category', models.CharField(choices=[('AGG', 'Aggregate'), ('CEM', 'Cement'), ('ADD', 'Additive'), ('WAT', 'Water')], default='AGG', max_length=3)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('unit', models.CharField(blank=True, max_length=10)),
                ('agg_size', models.IntegerField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('plc_ref', models.IntegerField(unique=True)),
                ('name', models.CharField(default='', max_length=50)),
                ('description', models.CharField(blank=True, max_length=50)),
                ('usage_ratio', models.IntegerField()),
                ('current_ingredient', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='batches.Ingredient')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('slump_class', models.CharField(max_length=10)),
                ('exposure_class', models.CharField(max_length=10)),
                ('cl_content_class', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='Recipe_Detail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batches.Ingredient')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='batches.Recipe')),
            ],
        ),
        migrations.CreateModel(
            name='Truck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reg', models.CharField(max_length=15)),
            ],
        ),
        migrations.AddField(
            model_name='drop_detail',
            name='ingredient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batches.Ingredient'),
        ),
        migrations.AddField(
            model_name='drop_detail',
            name='used_location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batches.Location'),
        ),
        migrations.AddField(
            model_name='batch',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batches.Client'),
        ),
        migrations.AddField(
            model_name='batch',
            name='driver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batches.Driver'),
        ),
        migrations.AddField(
            model_name='batch',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batches.Recipe'),
        ),
        migrations.AddField(
            model_name='batch',
            name='truck',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='batches.Truck'),
        ),
    ]