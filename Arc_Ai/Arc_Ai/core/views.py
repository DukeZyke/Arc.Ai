from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from .models import Email, Project, PersonalInformation, EmployeeAward



def profilepage(request):
    projects = Project.objects.all()
    personal_information = PersonalInformation.objects.first()
    employee_awards = EmployeeAward.objects.all()

    return render(request, 'core/profilepage.html', {
        'projects' : projects,
        'personal_information' : personal_information,
        'employee_awards' : employee_awards,
        })

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Authenticate user
        user = authenticate(email=email, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, 'You have successfully logged in.')
            return redirect('core:home')  # Redirect to a valid URL name
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
            return redirect('core:login')  # Redirect back to login page

    return render(request, 'core/login.html')


def signup(request):
    if request.method == 'POST':
        print(request.POST)
        # Extracting data from the form
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Your passwords do not match. Please try again.')
            return redirect('core:signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already taken. Please try again.')
            return redirect('core:signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken. Please try again.')
            return redirect('core:signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'Account created successfully. You can now log in.')
        return redirect('core:login')

    return render(request, 'core/signup.html')


from allauth.account.views import SignupView

class CustomSignupView(SignupView):
    def get(self, *args, **kwargs):
        # Add any custom logic here if needed
        return super().get(*args, **kwargs)

def home(request):
    return render(request, 'core/home.html')

def organization(request):
    projects = Project.objects.all()
    personal_information = PersonalInformation.objects.first()
    employee_awards = EmployeeAward.objects.all()

    return render(request, 'core/organization.html', {
        'projects' : projects,
        'personal_information' : personal_information,
        'employee_awards' : employee_awards,
        })

def saved(request):
# Simulated backend data
    folders = [f"Folder {i}" for i in range(1, 21)]  # 20 folders
    files = [f"File {i}" for i in range(1, 21)]      # 20 files
    trash = [f"Trash File {i}" for i in range(1, 21)] # 20 trash files

    # Pass the data to the template
    return render(request, 'core/saved.html', {
        'folders': folders,
        'files': files,
        'trash': trash,
    })

def email(request):
    online_users = ["Alice", "Bob", "Charlie", "Diana", "Eve", "Frank", "Grace", "Heidi", "Ivan", "Judy"]  # Simulated online users
    emails = Email.objects.all()  # Fetch all emails from the database

    return render(request, 'core/email.html', {
        'online_users': online_users,
        'emails': emails,
    })

def landingpage(request):
    return render(request, 'core/landingpage.html')