# Generated by Django 5.1.1 on 2024-11-30 21:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_alter_todo_description"),
    ]

    operations = [
        migrations.AlterField(
            model_name="todo",
            name="tags",
            field=models.ManyToManyField(
                blank=True,
                help_text="Optional tags associated with the task",
                related_name="todos",
                to="core.tag",
            ),
        ),
    ]
