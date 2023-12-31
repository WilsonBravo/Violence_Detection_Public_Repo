# Generated by Django 4.2.5 on 2023-10-03 01:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_alter_configuraciones_del_sistema_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='configuraciones_generales',
            name='ip_addr_server',
        ),
        migrations.AddField(
            model_name='configuraciones_del_sistema',
            name='camara_fps',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='configuraciones_generales',
            name='Interfaz',
            field=models.CharField(blank=True, choices=[('wifi', 'Wi-Fi'), ('ethernet', 'Ethernet')], max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='configuraciones_generales',
            name='message_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
