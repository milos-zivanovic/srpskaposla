# Generated by Django 3.0.5 on 2020-04-08 14:33

from django.db import migrations
from random import randint


def execute(apps, schema_editor):
    # Get models
    Job = apps.get_model('jobs', 'Job')

    # Update data
    for j in Job.objects.all():
        number = randint(1, 100)
        j.start_count = number
        j.count = number
        j.save()


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0007_job_start_count'),
    ]

    operations = [
        migrations.RunPython(execute),
    ]
