from django.shortcuts import render

def login(request):
    return render(request, 'core/login.html')

def signup(request):
    return render(request, 'core/signup.html')

def home(request):
    return render(request, 'core/home.html')

def organization(request):
    return render(request, 'core/organization.html')

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
    return render(request, 'core/email.html')
