from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('academy', '0018_alter_lesson_options_lesson_content_lesson_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='pdf_file',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='lesson_pdfs/',
                validators=[django.core.validators.FileExtensionValidator(['pdf'])],
                help_text='Ajoute yon dokiman PDF pou leson an si sa nesesè.',
            ),
        ),
    ]
