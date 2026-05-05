from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("academy", "0018_alter_lesson_options_lesson_content_lesson_order"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SeminarRegistration",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("motivation", models.TextField(blank=True, help_text="Poukisa ou vle patisipe nan seminè sa a?")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("seminar", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="registrations", to="academy.seminar")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="seminar_registrations", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ["-created_at"],
                "unique_together": {("user", "seminar")},
            },
        ),
    ]
