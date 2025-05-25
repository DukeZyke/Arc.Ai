from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User



class Email(models.Model):
    sender_name = models.CharField(max_length=100)
    sender_icon = models.ImageField(upload_to='icons/')
    title = models.CharField(max_length=200)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    

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
    name = models.CharField(max_length=100, default='Enter your name')
    email = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20)
    age = models.CharField(max_length=3)
    birth_date = models.DateField(max_length=20)
    gender = models.CharField(max_length=10)
    user_title = models.CharField(max_length=30)

    def __str__(self):
        return self.name
    

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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drive_files')
    name = models.CharField(max_length=255)
    file_id = models.CharField(max_length=255, db_index=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class DriveFolder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='drive_folders')
    name = models.CharField(max_length=255)
    folder_id = models.CharField(max_length=255, db_index=True)
    parent_folder_id = models.CharField(max_length=255, blank=True, null=True)  # For folder hierarchy
    created_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='folders', null=True, blank=True)  # <-- Add this line
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    

class SignupDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='signup_details')
    profile_avatar_id = models.IntegerField(default=1)  # Save avatar as id (1-15)
    first_name = models.CharField(max_length=255)
    middle_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    complete_address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=255)
    age = models.CharField(max_length=3)
    gender = models.CharField(max_length=255)
    position = models.CharField(max_length=100, default="No position yet")
    department = models.CharField(max_length=100, default="No position yet")

    @property
    def avatar_url(self):
        return f'/static/Images/Profile{self.profile_avatar_id}.png'

    
# For notification sidebar Popup TEST
class Notification(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    posted_by = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=now)

    def __str__(self):
        return self.title


class Project(models.Model):
    name = models.CharField(max_length=100)
    project_desc = models.CharField(max_length=100, blank=True, default='No description provided')
    # Remove project_id field!
    start_date = models.DateField(max_length=20)
    finish_date = models.DateField(max_length=20)
    project_status = models.CharField(max_length=50)
    project_manager = models.CharField(max_length=100)

    @property
    def project_id_str(self):
        return f"HR-2024-ONB-{self.id:02d}"
    

    def __str__(self):
        return f"{self.name} {self.project_id_str}"
    
class ProjectMember(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='members')
    member_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.member_name} ({self.project.name})"
    

    
# class CreateProject(models.Model):
#     project = models.OneToOneField(Project, on_delete=models.CASCADE) 
#     project_members = super(Project.project_members)

#     for members in project_members:
#         member_names = models.CharField(max_length=200)

# class EditProject(models.Model):
#     project = models.OneToOneField(Project, on_delete=models.CASCADE)


