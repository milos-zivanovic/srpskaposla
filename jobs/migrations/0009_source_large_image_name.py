# Generated by Django 3.0.5 on 2020-04-17 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0008_auto_20200408_1633'),
    ]

    operations = [
        migrations.AddField(
            model_name='source',
            name='large_image_name',
            field=models.CharField(max_length=75, null=True),
        ),
    ]
