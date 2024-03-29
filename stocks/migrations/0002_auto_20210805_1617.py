# Generated by Django 3.2.5 on 2021-08-05 15:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stock',
            name='ticker1',
        ),
        migrations.RemoveField(
            model_name='stock',
            name='ticker2',
        ),
        migrations.AddField(
            model_name='stock',
            name='stock_id',
            field=models.CharField(default=1, max_length=1000),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='stock',
            name='stock_value',
            field=models.CharField(default=1, max_length=100),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_name', models.CharField(max_length=1000)),
                ('text_value', models.CharField(max_length=100)),
                ('stock_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stocks.stock')),
            ],
        ),
    ]
