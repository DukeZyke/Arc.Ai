from django.contrib import admin
from .models import Project, PersonalInformation, EmployeeAward, DriveFile, SignupDetails, Email, Notification

# Profile page
admin.site.register(Project)
admin.site.register(PersonalInformation)
admin.site.register(EmployeeAward)

# Saved Page    
admin.site.register(DriveFile)

# Signup Page
admin.site.register(SignupDetails)

# Email Page
admin.site.register(Email)

# Sidebar Page
admin.site.register(Notification)