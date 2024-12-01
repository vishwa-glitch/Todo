# Generated by Django 5.1.1 on 2024-11-28 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.CreateModel(
            name='Todo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(max_length=100)),
                ('description', models.TextField(max_length=1000)),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('OPEN', 'Open'), ('WORKING', 'Working'), ('PENDING_REVIEW', 'Pending Review'), ('COMPLETED', 'Completed'), ('OVERDUE', 'Overdue'), ('CANCELLED', 'Cancelled')], default='OPEN', max_length=20)),
                ('tags', models.ManyToManyField(blank=True, to='core.tag')),
            ],
            options={
                'verbose_name': 'Todo Item',
                'verbose_name_plural': 'Todo Items',
                'ordering': ['-created_at'],
            },
        ),
    ]
