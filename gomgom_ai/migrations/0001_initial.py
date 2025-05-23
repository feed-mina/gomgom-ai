# Generated by Django 5.2 on 2025-04-26 09:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recommendation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('input_text', models.TextField()),
                ('selected_types', models.JSONField()),
                ('recommended_store', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('category', models.CharField(max_length=255)),
                ('keywords', models.JSONField()),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('user_ip', models.GenericIPAddressField(blank=True, null=True)),
                ('is_success', models.BooleanField(default=True)),
                ('gpt_raw_response', models.JSONField(blank=True, null=True)),
                ('matched_restaurant_id', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
