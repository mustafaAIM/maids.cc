# Generated by Django 5.1.2 on 2025-03-15 11:42

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('books', '0002_alter_book_options_remove_book_available_quantity_and_more'),
        ('patrons', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BorrowingRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('borrow_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Borrow Date')),
                ('due_date', models.DateTimeField(verbose_name='Due Date')),
                ('return_date', models.DateTimeField(blank=True, null=True, verbose_name='Return Date')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('borrowed', 'Borrowed'), ('returned', 'Returned'), ('overdue', 'Overdue')], default='pending', max_length=10, verbose_name='Status')),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borrowing_records', to='books.book')),
                ('patron', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='borrowing_records', to='patrons.patron')),
            ],
            options={
                'verbose_name': 'Borrowing Record',
                'verbose_name_plural': 'Borrowing Records',
                'ordering': ['-borrow_date'],
                'indexes': [models.Index(fields=['status'], name='borrowings__status_b39208_idx'), models.Index(fields=['due_date'], name='borrowings__due_dat_446a8e_idx')],
            },
        ),
    ]
