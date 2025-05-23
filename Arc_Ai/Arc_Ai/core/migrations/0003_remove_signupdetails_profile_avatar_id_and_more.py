from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20250523_0306'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='signupdetails',
            name='profile_avatar_id',
        ),
        migrations.AddField(
            model_name='signupdetails',
            name='avatar',
            field=models.CharField(choices=[('Profile1.png', 'Avatar 1'), ('Profile2.png', 'Avatar 2'), ('Profile3.png', 'Avatar 3'), ('Profile4.png', 'Avatar 4'), ('Profile5.png', 'Avatar 5'), ('Profile6.png', 'Avatar 6'), ('Profile7.png', 'Avatar 7'), ('Profile8.png', 'Avatar 8'), ('Profile9.png', 'Avatar 9'), ('Profile10.png', 'Avatar 10'), ('Profile11.png', 'Avatar 11'), ('Profile12.png', 'Avatar 12'), ('Profile13.png', 'Avatar 13'), ('Profile14.png', 'Avatar 14'), ('Profile15.png', 'Avatar 15')], default='Profile1.png', max_length=100),
        ),
    ]
