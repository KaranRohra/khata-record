# Generated by Django 3.2 on 2021-04-25 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creator_email', models.EmailField(max_length=100)),
                ('creator_name', models.CharField(max_length=100)),
                ('receiver_email', models.EmailField(max_length=100)),
                ('receiver_name', models.EmailField(max_length=100)),
                ('amount', models.IntegerField()),
                ('product', models.CharField(max_length=100)),
                ('due_date', models.DateField()),
                ('created_at', models.DateTimeField()),
                ('status', models.CharField(default='Pending', max_length=20)),
                ('message', models.CharField(default='Message not available', max_length=200)),
            ],
            options={
                'db_table': 'bill',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('from_email', models.EmailField(max_length=100)),
                ('to_email', models.EmailField(max_length=100)),
                ('created_at', models.DateTimeField()),
                ('bill_id', models.IntegerField()),
            ],
            options={
                'db_table': 'notification',
            },
        ),
    ]
