from django.contrib import admin
from .models import Project, PersonalInformation, EmployeeAward, DriveFile, DriveFolder, SignupDetails, Email, Notification, ProjectMember

# Profile page
# admin.site.register(Project)
admin.site.register(PersonalInformation)
admin.site.register(EmployeeAward)

# Saved Page    
admin.site.register(DriveFile)
admin.site.register(DriveFolder)

# Signup Page
admin.site.register(SignupDetails)

# Email Page
admin.site.register(Email)

# Sidebar Page
admin.site.register(Notification)

# Admin User Profile Page
class ProjectMemberInline(admin.TabularInline):  # or admin.StackedInline
    model = ProjectMember
    extra = 1  # Number of empty forms to display

class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectMemberInline]
    
admin.site.register(Project, ProjectAdmin)
# admin.site.register(ProjectMember)
