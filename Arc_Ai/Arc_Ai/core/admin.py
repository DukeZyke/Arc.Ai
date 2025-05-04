from django.contrib import admin
from .models import Project, PersonalInformation, EmployeeAward

# Register your models here.

# Profile page
admin.site.register(Project)
admin.site.register(PersonalInformation)
admin.site.register(EmployeeAward)
