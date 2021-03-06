# Generated by Django 2.1 on 2019-08-09 14:25

import beerlab.fermentable
from django.db import migrations, models
import django.db.models.deletion
import unicorn.models.base
import unicorn.models.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractUnit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True, verbose_name='Name')),
                ('synonyms', models.CharField(blank=True, max_length=255, null=True, verbose_name='Synonyms')),
            ],
            options={
                'verbose_name_plural': 'Units',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Conversion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_amount', models.FloatField(default=1.0, verbose_name='From amount')),
                ('to_amount', models.FloatField(default=1.0, verbose_name='To amount')),
                ('marker', models.CharField(choices=[('<', '<'), ('=', '='), ('>', '>')], default='=', max_length=1, verbose_name='Marker')),
                ('generic', models.BooleanField(default=False, verbose_name='Generic')),
                ('year_from', models.SmallIntegerField(blank=True, null=True, verbose_name='From year')),
                ('year_to', models.SmallIntegerField(blank=True, null=True, verbose_name='To year')),
                ('original_text', models.TextField(blank=True, null=True, verbose_name='Original text')),
                ('precision', models.FloatField(blank=True, null=True, validators=[unicorn.models.validators.is_range_01])),
                ('status', models.SmallIntegerField(choices=[(1, 'Reference'), (2, 'Inferred'), (3, 'Ambiguous'), (4, 'Asumption'), (5, 'Anomalous'), (-1, 'Error'), (-2, 'Irrelevant')], default=1, verbose_name='Status')),
            ],
            options={
                'ordering': ['from_unit__name'],
            },
            bases=(models.Model, unicorn.models.base.CacheKeyMixin),
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Name')),
                ('synonyms', models.CharField(blank=True, max_length=255, null=True, verbose_name='Synonyms')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('synonyms', models.CharField(blank=True, max_length=255, null=True, verbose_name='Synonyms')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Date')),
                ('year', models.SmallIntegerField(verbose_name='Year of publication')),
                ('info', models.TextField(blank=True, null=True, verbose_name='Information')),
                ('amount', models.FloatField(verbose_name='Yield amount')),
            ],
            options={
                'verbose_name': 'Recipe',
                'verbose_name_plural': 'Recipes',
                'ordering': ['style__name', 'date'],
            },
        ),
        migrations.CreateModel(
            name='RecipeMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(verbose_name='Amount')),
                ('malted', models.BooleanField(default=False, verbose_name='Malted')),
            ],
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('year', models.SmallIntegerField(blank=True, null=True, verbose_name='Year of publication')),
                ('author', models.CharField(blank=True, max_length=255, null=True, verbose_name='Author')),
                ('publisher', models.CharField(blank=True, max_length=255, null=True, verbose_name='Publisher')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('enabled', models.BooleanField(default=True, verbose_name='Enabled')),
            ],
            options={
                'ordering': ['title'],
            },
        ),
        migrations.CreateModel(
            name='Style',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('synonyms', models.CharField(blank=True, max_length=255, null=True, verbose_name='Synonyms')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='SubConversion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(verbose_name='Amount')),
                ('operator', models.CharField(choices=[('+', '+'), ('-', '-')], max_length=1, verbose_name='Operator')),
                ('conversion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unicorn.Conversion')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_unicorn.subconversion_set+', to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='BaseUnit',
            fields=[
                ('abstractunit_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='unicorn.AbstractUnit')),
                ('quantity', models.SmallIntegerField(choices=[(1, 'Mass'), (2, 'Volume')], default=2, verbose_name='Quantity')),
            ],
            options={
                'verbose_name_plural': 'Units',
                'ordering': ['name'],
            },
            bases=('unicorn.abstractunit',),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('material_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='unicorn.Material')),
            ],
            options={
                'verbose_name_plural': 'Categories',
                'ordering': ['name'],
            },
            bases=('unicorn.material',),
        ),
        migrations.CreateModel(
            name='Fermentable',
            fields=[
                ('material_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='unicorn.Material')),
                ('extract', models.FloatField(default=0.8, verbose_name='Potential extract')),
                ('categories', models.ManyToManyField(blank=True, to='unicorn.Category')),
            ],
            options={
                'verbose_name_plural': 'Fermentables',
                'ordering': ['name'],
            },
            bases=(beerlab.fermentable.FermentableMixin, 'unicorn.material'),
        ),
        migrations.CreateModel(
            name='Hop',
            fields=[
                ('material_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='unicorn.Material')),
                ('alfa_acid', models.FloatField(default=5.0, verbose_name='Alfa acid')),
                ('categories', models.ManyToManyField(blank=True, to='unicorn.Category')),
            ],
            options={
                'verbose_name_plural': 'Hop',
                'ordering': ['name'],
            },
            bases=('unicorn.material',),
        ),
        migrations.CreateModel(
            name='LocalUnit',
            fields=[
                ('abstractunit_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='unicorn.AbstractUnit')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unicorn.Location', verbose_name='Location')),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unicorn.BaseUnit', verbose_name='Base unit')),
            ],
            options={
                'verbose_name_plural': 'Local units',
                'ordering': ['unit__name', 'location__name'],
            },
            bases=('unicorn.abstractunit',),
        ),
        migrations.CreateModel(
            name='Nonfermentable',
            fields=[
                ('material_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='unicorn.Material')),
                ('categories', models.ManyToManyField(blank=True, to='unicorn.Category')),
            ],
            options={
                'verbose_name_plural': 'Nonfermentables',
                'ordering': ['name'],
            },
            bases=('unicorn.material',),
        ),
        migrations.AddField(
            model_name='subconversion',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unicorn.AbstractUnit'),
        ),
        migrations.AddField(
            model_name='recipematerial',
            name='material',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unicorn.Material'),
        ),
        migrations.AddField(
            model_name='recipematerial',
            name='recepy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unicorn.Recipe'),
        ),
        migrations.AddField(
            model_name='recipematerial',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unicorn.AbstractUnit'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='amount_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unicorn.AbstractUnit', verbose_name='Yield unit'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='location',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unicorn.Location', verbose_name='Location'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='material',
            field=models.ManyToManyField(through='unicorn.RecipeMaterial', to='unicorn.Material'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unicorn.Source', verbose_name='Source'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='style',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='unicorn.Style', verbose_name='Style'),
        ),
        migrations.AddField(
            model_name='material',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_unicorn.material_set+', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='conversion',
            name='from_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversion_set', to='unicorn.AbstractUnit', verbose_name='From unit'),
        ),
        migrations.AddField(
            model_name='conversion',
            name='material',
            field=models.ManyToManyField(blank=True, to='unicorn.Material'),
        ),
        migrations.AddField(
            model_name='conversion',
            name='source',
            field=models.ManyToManyField(to='unicorn.Source'),
        ),
        migrations.AddField(
            model_name='conversion',
            name='to_unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='conversion_set_reverse', to='unicorn.AbstractUnit', verbose_name='To unit'),
        ),
        migrations.AddField(
            model_name='abstractunit',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='polymorphic_unicorn.abstractunit_set+', to='contenttypes.ContentType'),
        ),
    ]
