from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            "DROP TABLE IF EXISTS core_signupdetails;"
        ),
        migrations.CreateModel(
            name='SignupDetails',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profile_avatar_id', models.IntegerField(default=1)),  # Save avatar as id (1-15)
                ('first_name', models.CharField(max_length=255)),
                ('middle_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('complete_address', models.CharField(max_length=255)),
                ('contact_number', models.CharField(max_length=255)),
                ('age', models.CharField(max_length=3)),
                ('gender', models.CharField(max_length=255)),
                ('position', models.CharField(blank=True, default='No position provided', max_length=100, null=True)),
                ('department', models.CharField(blank=True, default='No department provided', max_length=100, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='signup_details', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]