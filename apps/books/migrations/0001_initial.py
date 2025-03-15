# Generated by Django 5.1.2 on 2025-03-14 12:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('author', models.CharField(max_length=255, verbose_name='Author')),
                ('isbn', models.CharField(max_length=13, unique=True, verbose_name='ISBN')),
                ('publication_year', models.IntegerField(validators=[django.core.validators.MinValueValidator(1000), django.core.validators.MaxValueValidator(9999)], verbose_name='Publication Year')),
                ('quantity', models.PositiveIntegerField(default=1, verbose_name='Quantity')),
                ('available_quantity', models.PositiveIntegerField(verbose_name='Available Quantity')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
            ],
            options={
                'verbose_name': 'Book',
                'verbose_name_plural': 'Books',
                'ordering': ['-created_at'],
            },
        ),
    ]
