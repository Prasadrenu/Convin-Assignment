# Generated by Django 5.0.7 on 2024-07-29 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0003_rename_description_expense_event_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expense',
            name='user_id',
            field=models.CharField(max_length=10),
        ),
    ]
