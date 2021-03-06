# Generated by Django 3.0.5 on 2020-04-17 11:02

from django.db import migrations


def execute(apps, schema_editor):
    # Get models
    Source = apps.get_model('jobs', 'Source')

    # Update data
    for s in Source.objects.all():
        name = s.name.lower()
        s.large_image_name = f'{name}-large.png'
        s.save()


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0009_source_large_image_name'),
    ]

    operations = [
        migrations.RunPython(execute),
    ]
