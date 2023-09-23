# Generated by Django 4.1.5 on 2023-06-19 02:46

from django.db import migrations, models
import django.db.models.deletion
import shopapp.models


class Migration(migrations.Migration):

    dependencies = [
        ('shopapp', '0003_product_preview'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to=shopapp.models.product_images_directory_path)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='shopapp.product')),
            ],
        ),
    ]
