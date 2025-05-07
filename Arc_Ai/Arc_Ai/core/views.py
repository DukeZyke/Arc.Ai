from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Email, Project, PersonalInformation, EmployeeAward

def signup_details(request):
    return render(request, 'core/signup_details.html', {
        'range': range(1, 16)  # Pass numbers 1 to 15 to the template
    })

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
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email=email, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('core/signup')
        else:
            messages.info(request, 'Credentials Invalid.')
            return redirect('core/login')

    return render(request, 'core/login.html')

def signup(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email is Already Taken. Try Again.')
                return redirect('core/signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username is Already Taken. Try Again.')
                return redirect('core/signup')
            else:
                user = User.objects.create_user(email=email,username=username, password=password)
                user.save();
                return redirect('core/login')
        else:
            messages.info(request, 'Your Passwords Do Not Match. Try Again.')
            return redirect('core/signup')
    else:
        return render(request, 'core/signup.html')

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