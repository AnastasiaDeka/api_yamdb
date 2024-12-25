# Generated by Django 3.2 on 2024-12-25 16:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_rename_created_comment_pub_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('name', 'slug')},
        ),
        migrations.AlterModelOptions(
            name='genre',
            options={'ordering': ('name', 'slug')},
        ),
        migrations.AlterModelOptions(
            name='title',
            options={'ordering': ('name', 'year')},
        ),
        migrations.RemoveField(
            model_name='title',
            name='rating',
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(unique=True, validators=[django.core.validators.RegexValidator(message='Слаг может содержать только буквы,цифры, подчеркивания и дефисы', regex='^[-a-zA-Z0-9_]+$')]),
        ),
        migrations.AlterField(
            model_name='genre',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='genre',
            name='slug',
            field=models.SlugField(unique=True, validators=[django.core.validators.RegexValidator(message='Слаг может содержать только буквы,цифры, подчеркивания и дефисы', regex='^[-a-zA-Z0-9_]+$')]),
        ),
        migrations.AlterField(
            model_name='title',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='title',
            name='name',
            field=models.CharField(max_length=256),
        ),
        migrations.AlterField(
            model_name='title',
            name='year',
            field=models.SmallIntegerField(validators=[django.core.validators.MaxValueValidator(2024, message='Год не может быть больше текущего')]),
        ),
    ]
