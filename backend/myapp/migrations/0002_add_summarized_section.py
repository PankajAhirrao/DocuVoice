# Generated manually for UserFile summarized_text and section fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userfile",
            name="summarized_text",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="userfile",
            name="section",
            field=models.CharField(blank=True, default="full_paper", max_length=64),
        ),
    ]
