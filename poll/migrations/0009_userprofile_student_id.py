# Generated by Django 5.2 on 2025-05-05 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0008_alter_userprofile_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='student_id',
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
