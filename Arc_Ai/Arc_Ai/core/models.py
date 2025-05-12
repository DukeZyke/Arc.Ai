from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Email(models.Model):
    sender_name = models.CharField(max_length=100)
    sender_icon = models.ImageField(upload_to='icons/')
    title = models.CharField(max_length=200)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
class Project(models.Model):
    name = models.CharField(max_length=100)
    project_id = models.CharField(max_length=20, unique=True, blank=True)
    start_date = models.DateField(max_length=20)
    finish_date = models.DateField(max_length=20)
    project_status = models.CharField(max_length=50)

    def save(self, *args, **kwargs):
        if not self.project_id:
            last_project = Project.objects.order_by('-id').first()
            if last_project and last_project.project_id:
                try:
                    last_number = int(last_project.project_id.split('-')[-1])
                    next_number = last_number + 1
                except:
                    next_number = 1
            else:
                next_number = 1

            self.project_id = f"{next_number:02d}"
        super().save(*args, **kwargs)

class PersonalInformation(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the User model
    email = models.EmailField(max_length=100)
    first_name = models.CharField(max_length=50)
    middle_initial = models.CharField(max_length=5, blank=True, null=True)
    last_name = models.CharField(max_length=50)
    complete_address = models.TextField()
    contact_number = models.CharField(max_length=20)
    age = models.IntegerField(validators=[MinValueValidator(0)])
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')]
    )
    department = models.CharField(max_length=50, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    profile_avatar = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class EmployeeAward(models.Model):
    award_classif = models.CharField(max_length=100)
    award_title = models.CharField(max_length=100)
    award_desc = models.CharField(max_length=200)
    award_date = models.DateField()

    ICONS = {
        'a': 'Images/Award_Trophy.png',
        'b': 'Images/Award_Teamwork.png',
        'c': 'Images/Award_Star.png',
    }

    @property
    def get_award_icon(self):
        return self.ICONS.get(self.award_classif.lower(), 'Images/Award_Trophy.png')

    def __str__(self):
        return f'{self.award_title} ({self.award_date})'

class DriveFile(models.Model):
    name = models.CharField(max_length=255)
    file_id = models.CharField(max_length=255, db_index=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class SignupDetails(models.Model):
    profile_avatar = models.ImageField(upload_to='avatars/')
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    complete_address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=255)
    gender = models.CharField(max_length=255)
    
# For notification sidebar Popup TEST
class Notification(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    posted_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.title
# =======================================================