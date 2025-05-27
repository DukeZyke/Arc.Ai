from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from .models import Notification
from django.utils.timezone import datetime
from django.contrib.auth import logout
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
import json
from django.db import models


# MODELS
from .models import Email, Project, PersonalInformation, EmployeeAward, DriveFile, SignupDetails, DriveFolder
from google_auth_oauthlib.flow import Flow
import os
from django.conf import settings
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from django.shortcuts import render, redirect
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import tempfile
import google.oauth2.credentials
import googleapiclient.discovery
from googleapiclient.http import MediaIoBaseUpload
import io
from io import BytesIO
from googleapiclient.errors import HttpError
from django.contrib.auth.decorators import login_required



GOOGLE_CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'secret', 'client_secret.json')

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file"
]

ROOT_FOLDER_ID = '1wdS3rmcuuiZ-mr2aH7SfYSTAF6Uvlv5z'

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# This is for local development only. In production, use HTTPS.



@login_required
def create_project_details(request):
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    from datetime import datetime as dt
    
    # Get all users with signup details for the dropdown
    available_users = SignupDetails.objects.select_related('user').all().order_by('first_name', 'last_name')
    
    # Create a safe JSON version of the data
    available_users_json = []
    for user_detail in available_users:
        available_users_json.append({
            'id': user_detail.user.id,
            'name': f"{user_detail.first_name} {user_detail.last_name}",
            'department': user_detail.department or "No Dept",
            'position': user_detail.position or "No Position"
        })
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('project_desc')
        start_date_str = request.POST.get('start_date')
        finish_date_str = request.POST.get('finish_date')
        status = request.POST.get('project_status')
        project_manager = request.POST.get('project_manager')
        member_user_ids = request.POST.getlist('member_user_ids')
        uploaded_files = request.FILES.getlist('add_file')

        # Handle date fields properly - convert empty strings to None
        start_date = None
        finish_date = None
        
        if start_date_str and start_date_str.strip():
            try:
                start_date = dt.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Invalid start date format. Please use YYYY-MM-DD format.")
                return render(request, 'core/create_project_details.html', {
                    'available_users': available_users,
                    'available_users_json': json.dumps(available_users_json),
                })
        
        if finish_date_str and finish_date_str.strip():
            try:
                finish_date = dt.strptime(finish_date_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Invalid finish date format. Please use YYYY-MM-DD format.")
                return render(request, 'core/create_project_details.html', {
                    'available_users': available_users,
                    'available_users_json': json.dumps(available_users_json),
                })

        # Validation: Check if required fields are filled
        if not name or not name.strip():
            messages.error(request, "Project name is required.")
            return render(request, 'core/create_project_details.html', {
                'available_users': available_users,
                'available_users_json': json.dumps(available_users_json),
            })

        if not project_manager:
            messages.error(request, "Project manager is required.")
            return render(request, 'core/create_project_details.html', {
                'available_users': available_users,
                'available_users_json': json.dumps(available_users_json),
            })

        # Check if user has Google Drive authorization
        creds_data = request.session.get('credentials')
        if not creds_data:
            messages.error(request, "You must authorize Google Drive access first to create project folders.")
            return redirect('core:google_drive_auth')

        try:
            # Create project - project_id will be auto-generated by the save method
            project = Project.objects.create(
                name=name.strip(),
                project_desc=description.strip() if description else '',
                start_date=start_date,  # Will be None if not provided
                finish_date=finish_date,  # Will be None if not provided
                project_status=status or 'Ongoing',
                project_manager=project_manager.strip()
                # project_id will be auto-generated, don't pass it
            )

            # Create project members using user IDs
            for user_id in member_user_ids:
                if user_id and user_id.strip():
                    try:
                        user = User.objects.get(id=user_id)
                        signup_details = user.signup_details
                        member_name = f"{signup_details.first_name} {signup_details.last_name}"
                        ProjectMember.objects.create(project=project, member_name=member_name)
                    except (User.DoesNotExist, SignupDetails.DoesNotExist):
                        continue

            # Google Drive folder creation
            PROJECT_PARENT_FOLDER_ID = '11tTPVSxTq87eF_pp9BQ3ud-XAsHw86mM'
            
            creds = Credentials(**creds_data)
            service = build('drive', 'v3', credentials=creds)

            # Create project folder
            folder_metadata = {
                'name': name.strip(),
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [PROJECT_PARENT_FOLDER_ID]
            }

            project_folder = service.files().create(
                body=folder_metadata,
                fields='id, name'
            ).execute()

            # Get current user's level and department for folder tracking
            try:
                signup_details = request.user.signup_details
                user_level = signup_details.user_level
                user_department = signup_details.department
            except SignupDetails.DoesNotExist:
                user_level = 1
                user_department = "Not specified"

            # Save project folder to database
            project_drive_folder = DriveFolder.objects.create(
                user=request.user,
                name=project_folder['name'],
                folder_id=project_folder['id'],
                parent_folder_id=PROJECT_PARENT_FOLDER_ID,
                creator_user_level=user_level,
                creator_department=user_department
            )

            # Upload files to the project folder if any
            if uploaded_files:
                for uploaded_file in uploaded_files:
                    file_metadata = {
                        'name': uploaded_file.name,
                        'parents': [project_folder['id']]
                    }
                    
                    media = MediaIoBaseUpload(
                        BytesIO(uploaded_file.read()),
                        mimetype=uploaded_file.content_type,
                        resumable=True
                    )
                    
                    uploaded_drive_file = service.files().create(
                        body=file_metadata,
                        media_body=media,
                        fields='id'
                    ).execute()
                    
                    DriveFile.objects.create(
                        user=request.user,
                        name=uploaded_file.name,
                        file_id=uploaded_drive_file.get('id'),
                        uploader_user_level=user_level,
                        uploader_department=user_department
                    )

            messages.success(request, f"Project '{name}' created successfully with folder '{project_folder['name']}'!")
            
            if uploaded_files:
                messages.info(request, f"Uploaded {len(uploaded_files)} file(s) to the project folder.")

        except Exception as e:
            print(f"Error creating project: {str(e)}")
            messages.error(request, f"Error creating project: {str(e)}")
            return render(request, 'core/create_project_details.html', {
                'available_users': available_users,
                'available_users_json': json.dumps(available_users_json),
            })

        return redirect('core:organization')

    return render(request, 'core/create_project_details.html', {
        'available_users': available_users,
        'available_users_json': json.dumps(available_users_json),
    })


def user_involved_map(request):
    return render(request, 'core/user_involved_map.html')

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import SignupDetails  # Make sure you have this

@login_required
def edit_user_profile(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    try:
        signup_details = SignupDetails.objects.get(user=user)
    except SignupDetails.DoesNotExist:
        signup_details = SignupDetails(user=user)  # Create if missing

    if request.method == 'POST':
        # Update User model
        user.email = request.POST.get('email')
        user.save()

        # Update SignupDetails
        signup_details.first_name = request.POST.get('first_name')
        signup_details.middle_name = request.POST.get('middle_name')
        signup_details.last_name = request.POST.get('last_name')
        signup_details.complete_address = request.POST.get('complete_address')
        signup_details.contact_number = request.POST.get('contact_number')
        signup_details.age = request.POST.get('age')
        signup_details.gender = request.POST.get('gender')
        signup_details.position = request.POST.get('position')
        signup_details.department = request.POST.get('department')

        # Save selected avatar
        avatar_id = request.POST.get('profile_avatar_id', 1)
        signup_details.profile_avatar_id = int(avatar_id)

        signup_details.save()

        # Update user permissions based on position
        position = request.POST.get('position')
        
        if position == "Executive Position":
            user.is_superuser = True
            user.is_staff = True
        elif position == "Dept. Manager":
            user.is_superuser = False
            user.is_staff = True  
        elif position == "Supervisor":
            user.is_superuser = False
            user.is_staff = True
        else:  # Employee
            user.is_superuser = False
            user.is_staff = False
        
        user.save()

        return redirect('core:profilepage', pk=user.pk)

    return render(request, 'core/edit_user_profile.html', {
        'signup_details': signup_details,
        'user': user,
        'range': range(1, 16)
    })

def admin_files_page(request):
    # Check admin privileges
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You need administrator privileges to access this page.")
        return redirect('core:login')
    
    # Get all users who have completed signup details
    signup_details = SignupDetails.objects.select_related('user').all().order_by('first_name', 'last_name')
    
    # Prepare data structure for users and their files
    user_files_data = []
    total_files = 0
    total_folders = 0
    total_size = 0  # in bytes
    
    # Check if Drive credentials are available for fetching additional file details
    creds_data = request.session.get('credentials')
    if creds_data:
        creds = Credentials(**creds_data)
        
        try:
            # Build the Drive service
            service = build('drive', 'v3', credentials=creds)
            
            # For each user with signup details, fetch their files and folders
            for detail in signup_details:
                user = detail.user
                
                # Get files and folders associated with this user from the database
                user_drive_files = DriveFile.objects.filter(user=user).order_by('-uploaded_at')
                user_drive_folders = DriveFolder.objects.filter(user=user).order_by('-created_at')
                
                # Initialize lists for files and folders
                files = []
                folders = []
                user_total_size = 0
                
                # Process each file
                for drive_file in user_drive_files:
                    try:
                        # Get detailed file info from Drive
                        file_info = service.files().get(
                            fileId=drive_file.file_id, 
                            fields="name,mimeType,size,createdTime"
                        ).execute()
                        
                        file_size = int(file_info.get('size', 0)) if 'size' in file_info else 0
                        file_data = {
                            'id': drive_file.file_id,
                            'name': drive_file.name,
                            'date': drive_file.uploaded_at.strftime('%d %b %Y'),
                            'size': file_size,
                            'size_display': f"{file_size / 1024:.2f} kb" if file_size > 0 else 'N/A'
                        }
                        
                        files.append(file_data)
                        total_files += 1
                        total_size += file_size
                        user_total_size += file_size
                        
                    except Exception as e:
                        # If we can't get details from Drive, use what we have in the database
                        file_data = {
                            'id': drive_file.file_id,
                            'name': drive_file.name,
                            'date': drive_file.uploaded_at.strftime('%d %b %Y'),
                            'size': 0,
                            'size_display': 'N/A'
                        }
                        files.append(file_data)
                        total_files += 1
                
                # Process each folder
                for drive_folder in user_drive_folders:
                    folder_data = {
                        'id': drive_folder.folder_id,
                        'name': drive_folder.name,
                        'parent_id': drive_folder.parent_folder_id or 'Root',
                        'date': drive_folder.created_at.strftime('%d %b %Y'),
                        'size_display': 'Folder'
                    }
                    folders.append(folder_data)
                    total_folders += 1
                
                # Add user data with their files and folders using signup_details
                user_files_data.append({
                    'user': {
                        'id': user.id,
                        'name': f"{detail.first_name} {detail.last_name}",
                        'email': user.email,
                        'username': user.username,
                        'avatar': f'Images/Profile{detail.profile_avatar_id}.png',
                        'department': detail.department or "Not Set",
                        'position': detail.position or "Not Set",
                        'user_level': detail.user_level,
                        'contact_number': detail.contact_number,
                        'total_size': f"{user_total_size / (1024 * 1024):.2f} MB"
                    },
                    'signup_details': detail,  # Pass the signup details object
                    'files': files,
                    'folders': folders,
                    'file_count': len(files),
                    'folder_count': len(folders)
                })
                
        except Exception as e:
            print(f"Error processing files: {str(e)}")
            messages.error(request, f"Error retrieving files: {str(e)}")
    else:
        # If no Drive credentials, just get basic info from database
        for detail in signup_details:
            user = detail.user
            user_drive_files = DriveFile.objects.filter(user=user).order_by('-uploaded_at')
            user_drive_folders = DriveFolder.objects.filter(user=user).order_by('-created_at')
            
            files = [{
                'id': file.file_id,
                'name': file.name,
                'date': file.uploaded_at.strftime('%d %b %Y'),
                'size': 0,
                'size_display': 'Database only'
            } for file in user_drive_files]
            
            folders = [{
                'id': folder.folder_id,
                'name': folder.name,
                'parent_id': folder.parent_folder_id or 'Root',
                'date': folder.created_at.strftime('%d %b %Y'),
                'size_display': 'Folder'
            } for folder in user_drive_folders]
            
            total_files += len(files)
            total_folders += len(folders)
            
            user_files_data.append({
                'user': {
                    'id': user.id,
                    'name': f"{detail.first_name} {detail.last_name}",
                    'email': user.email,
                    'username': user.username,
                    'avatar': f'Images/Profile{detail.profile_avatar_id}.png',
                    'department': detail.department or "Not Set",
                    'position': detail.position or "Not Set",
                    'user_level': detail.user_level,
                    'contact_number': detail.contact_number,
                    'total_size': '0 MB'
                },
                'signup_details': detail,
                'files': files,
                'folders': folders,
                'file_count': len(files),
                'folder_count': len(folders)
            })
    
    return render(request, 'core/admin_files_page.html', {
        'users_data': user_files_data,
        'total_files': total_files,
        'total_folders': total_folders,
        'total_size': f"{total_size / (1024 * 1024):.2f} MB",
        'active_page': 'files',  # For highlighting the current page in navigation
    })

def admin_project_page(request):
    projects = Project.objects.all()

    # Check if user is authenticated and has admin privileges
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You need administrator privileges to access this page.")
        return redirect('core:login')  # Or redirect to home
    
    # Continue with the admin page view for authorized users
    return render(request,'core/admin_project_page.html', {
        'projects': projects
    })
    
def admin_users_page(request):
    # Check if user is authenticated and has admin privileges
    if not request.user.is_authenticated or not request.user.is_staff:
        messages.error(request, "You need administrator privileges to access this page.")
        return redirect('core:login')
    
    # Get all signup details (users who have completed registration)
    signup_details = SignupDetails.objects.select_related('user').all().order_by('first_name', 'last_name')
    
    # Create a list of users with their complete information
    users_with_details = []
    for detail in signup_details:
        users_with_details.append({
            'user': detail.user,
            'signup_details': detail,
            'full_name': f"{detail.first_name} {detail.last_name}",
            'department': detail.department or "Not Set",
            'position': detail.position or "Not Set",
            'user_level': detail.user_level,
        })
    
    context = {
        'users_with_details': users_with_details,
        'total_users': len(users_with_details),
        'active_users': len([u for u in users_with_details if u['user'].is_active]),
        'active_page': 'home',  # For navigation highlighting
    }
    return render(request, 'core/admin_users_page.html', context)


# =================================== FOR EDITING OF PROJECTS ===================================

from django.shortcuts import render, get_object_or_404, redirect
from .models import Project, ProjectMember


def admin_edit_project_details(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    members = project.members.all()

    if request.method == 'POST':
        # Update project fields
        project.name = request.POST.get('name')
        project.project_desc = request.POST.get('project_desc')
        project.start_date = request.POST.get('start_date')
        project.finish_date = request.POST.get('finish_date')   
        project.project_status = request.POST.get('project_status')
        project.project_manager = request.POST.get('project_manager')
        project.save()

        # Update members
        member_names = request.POST.getlist('member_names')
        # Remove all old members and add new ones
        project.members.all().delete()
        for name in member_names:
            if name.strip():
                ProjectMember.objects.create(project=project, member_name=name.strip())

        return redirect('core:admin_project_page')  # or wherever you want to go after saving

    return render(request, 'core/admin_edit_project_details.html', {
        'project': project,
        'members': members,
    })

# =================================== FOR EDITING OF PROJECTS ===================================

# =================================== FOR DELETING OF PROJECTS ===================================


def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    return redirect('core:admin_project_page')

# =================================== FOR DELETING OF PROJECTS ===================================

# =================================== FOR CREATION OF PROJECTS ===================================


# =================================== FOR CREATION OF PROJECTS ===================================







@login_required
def signup_details(request):
    if SignupDetails.objects.filter(user=request.user).exists():
        return redirect('core:profilepage', pk=request.user.pk)

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        complete_address = request.POST.get('complete_address')
        contact_number = request.POST.get('contact_number')
        age = request.POST.get('age')
        gender = request.POST.get('gender')
        department = request.POST.get('department')
        position = request.POST.get('position')
        user_level = request.POST.get('user_level')
        
        # Server-side validation: Executive Position can only be Administrative department
        if position == "Executive Position" and department != "Administrative (Main)":
            messages.error(request, "Executive Position can only be assigned to Administrative department.")
            return render(request, 'core/signup_details.html', {
                'range': range(1, 16)
            })
        
        # Double-check user_level based on position (server-side validation)
        if position == "Employee":
            user_level = 1
        elif position == "Supervisor":
            user_level = 2
        elif position == "Dept. Manager":
            user_level = 3
        elif position == "Executive Position":
            user_level = 4
            department = "Administrative"  # Force Administrative for Executive
        else:
            user_level = 1  # Default to Employee level
        
        # Debug: Print the values to check
        print(f"Position: {position}, Department: {department}, User Level: {user_level}")
        
        # Create or update SignupDetails for the logged-in user
        signup_details, created = SignupDetails.objects.update_or_create(
            user=request.user,
            defaults={
                'first_name': first_name,
                'middle_name': middle_name,
                'last_name': last_name,
                'complete_address': complete_address,
                'contact_number': contact_number,
                'age': age,
                'gender': gender,
                'department': department,
                'position': position,
                'user_level': user_level,
            }
        )

        # Update user permissions based on position
        if position == "Executive Position":
            request.user.is_superuser = True
            request.user.is_staff = True
        elif position == "Dept. Manager":
            request.user.is_superuser = False
            request.user.is_staff = True  
        elif position == "Supervisor":
            request.user.is_superuser = False
            request.user.is_staff = True
        else:  # Employee
            request.user.is_superuser = False
            request.user.is_staff = False
        
        request.user.save()

        messages.info(request, "Profile details saved successfully!")
        return redirect('core:profilepage', pk=request.user.pk)

    return render(request, 'core/signup_details.html', {
        'range': range(1, 16)
    })


@login_required 
def profilepage(request, pk):
    signup_details = None
    if request.user.is_authenticated:
        try:
            signup_details = request.user.signup_details
        except SignupDetails.DoesNotExist:
            signup_details = None

    # Filter projects to only show those where the user is involved
    user_projects = Project.objects.none()  # Start with empty queryset
    
    if signup_details:
        # Get current user's full name
        user_full_name = f"{signup_details.first_name} {signup_details.last_name}"
        
        # Filter projects where user is either project manager or team member
        user_projects = Project.objects.filter(
            models.Q(project_manager=user_full_name) |  # User is project manager
            models.Q(members__member_name=user_full_name)  # User is team member
        ).distinct().order_by('-id')
    
    employee_awards = EmployeeAward.objects.all()
    personal_information = PersonalInformation.objects.first()

    return render(request, 'core/profilepage.html', {
        'projects': user_projects,  # Changed from all projects to user's projects only
        'personal_information': personal_information,
        'employee_awards': employee_awards,
        'signup_details': signup_details,
        'active_page': 'profilepage'  # Added for navigation highlighting
    })

def landingpage(request):
    return render(request, 'core/landingpage.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('core:login')

def login(request):
    # Force logout if accessing login page directly
    if request.user.is_authenticated and request.method == 'GET':
        logout(request)
        request.session.flush()
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Find user by email first (keep your existing authentication logic)
        try:
            user = User.objects.get(email=email)
            user = authenticate(username=user.username, password=password)
            
            if user is not None:
                auth_login(request, user)
                
                # Set no-cache headers to prevent back button issues
                response = redirect('core:signup_details')  # <-- Redirect here
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
                return response
            else:
                messages.error(request, 'Invalid credentials. Please try again.')
        except User.DoesNotExist:
            messages.error(request, 'User not found.')
        
        return redirect('core:login')

    # Set no-cache headers even on GET requests
    response = render(request, 'core/login.html')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response


def admin_login(request):
    if request.method == 'POST':
        admin_email = request.POST.get('admin_email')
        admin_password = request.POST.get('admin_password')

        # Find user by email first
        try:
            user = User.objects.get(email=admin_email)
            # Authenticate with username and password
            user = authenticate(username=user.username, password=admin_password)
            
            if user is not None and (user.is_staff or user.is_superuser):
                auth_login(request, user)
                messages.success(request, 'Admin login successful.')
                return redirect('core:admin_project_page')
            else:
                messages.error(request, 'Invalid admin credentials or insufficient privileges.')
        except User.DoesNotExist:
            messages.error(request, 'Admin account not found.')
        
        return redirect('core:admin_login')

    return render(request, 'core/admin_login.html')


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

def admin_signup(request):
    if request.method == 'POST':
        # Extracting data from the form
        email = request.POST.get('admin_email')
        username = request.POST.get('admin_username')
        password = request.POST.get('admin_password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Your passwords do not match. Please try again.')
            return redirect('core:admin_signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already taken. Please try again.')
            return redirect('core:admin_signup')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already taken. Please try again.')
            return redirect('core:admin_signup')

        # Create a user with admin privileges
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True  # Grant staff permissions
        user.is_superuser = False  # Optional: can make True for full superuser privileges
        user.save()
        
        messages.success(request, 'Admin account created successfully. You can now log in.')
        return redirect('core:admin_login')

    return render(request, 'core/admin_signup.html')

# Add this helper function to your views.py
def is_admin(user):
    """Check if a user has admin privileges"""
    return user.is_authenticated and user.is_staff


from allauth.account.views import SignupView

class CustomSignupView(SignupView):
    def get(self, *args, **kwargs):
        # Add any custom logic here if needed
        return super().get(*args, **kwargs)

def home(request,):
    return render(request, 'core/home.html')

@login_required
def organization(request):
    try:
        # Get current user's full name from signup details
        user_signup_details = request.user.signup_details
        user_full_name = f"{user_signup_details.first_name} {user_signup_details.last_name}"
    except SignupDetails.DoesNotExist:
        messages.error(request, "Please complete your profile first.")
        return redirect('core:profilepage', pk=request.user.pk)
    
    # Filter projects where user is either project manager or team member
    user_projects = Project.objects.filter(
        models.Q(project_manager=user_full_name) |  # User is project manager
        models.Q(members__member_name=user_full_name)  # User is team member
    ).distinct().order_by('-id')
    
    # Get the most recent project for "Continue Working" section
    top_project = user_projects.first() if user_projects.exists() else None
    
    # Get all projects for the project list (excluding the top project)
    other_projects = user_projects.exclude(id=top_project.id) if top_project else user_projects
    
    context = {
        'top_project': top_project,
        'projects': other_projects,
        'active_page': 'organization'
    }
    
    return render(request, 'core/organization.html', context)

from django.http import JsonResponse
from .models import Project, ProjectMember

@login_required
def get_project_details(request, project_id):
    try:
        # Get current user's full name
        try:
            user_signup_details = request.user.signup_details
            user_full_name = f"{user_signup_details.first_name} {user_signup_details.last_name}"
        except SignupDetails.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User profile not complete'})
        
        # Get project and check if user has access
        project = Project.objects.get(pk=project_id)
        
        # Check if user is project manager or team member
        is_project_manager = project.project_manager == user_full_name
        is_team_member = ProjectMember.objects.filter(
            project=project,
            member_name=user_full_name
        ).exists()
        
        if not (is_project_manager or is_team_member):
            return JsonResponse({'success': False, 'error': 'Access denied: You are not part of this project'})
        
        members = list(project.members.values_list('member_name', flat=True))
        data = {
            'id': project.id,
            'name': project.name,
            'project_id_str': project.project_id_str,
            'project_desc': project.project_desc,
            'project_manager': project.project_manager,
            'start_date': project.start_date.strftime('%Y-%m-%d') if project.start_date else '-',
            'finish_date': project.finish_date.strftime('%Y-%m-%d') if project.finish_date else '-',
            'project_status': project.project_status,
            'members': members,
        }
        return JsonResponse({'success': True, 'project': data})
    except Project.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Project not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def landingpage(request):
    return render(request, 'core/landingpage.html')

def saved(request):
    folder_id = ROOT_FOLDER_ID
    user_id = request.GET.get('user_id')
    user_name = request.GET.get('user_name')
    
    creds_data = request.session.get('credentials')
    if not creds_data:
        messages.error(request, "You must authorize Google Drive to fetch files.")
        return redirect('core:google_drive_auth')

    creds = Credentials(**creds_data)

    try:
        service = build('drive', 'v3', credentials=creds)

        # Get accessible files and folders based on user level and department
        accessible_files, accessible_folders = get_accessible_files_for_user(request.user)
        
        # Get file IDs and folder IDs that user can access
        accessible_file_ids = set(accessible_files.values_list('file_id', flat=True))
        accessible_folder_ids = set(accessible_folders.values_list('folder_id', flat=True))

        # Fetch folders from Google Drive
        folder_results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
            pageSize=100,
            fields="files(id, name, parents)"
        ).execute()

        all_folders = folder_results.get('files', [])
        # Filter folders based on access rights
        filtered_folders = [folder for folder in all_folders if folder['id'] in accessible_folder_ids]

        # Get creator information from database with signup details for folders
        folder_id_to_creator_info = {}
        for folder_obj in accessible_folders:
            try:
                signup_details = folder_obj.user.signup_details
                creator_name = f"{signup_details.first_name} {signup_details.last_name}"
                creator_department = signup_details.department
            except SignupDetails.DoesNotExist:
                creator_name = folder_obj.user.username  # Fallback to username
                creator_department = "Not specified"
            
            folder_id_to_creator_info[folder_obj.folder_id] = {
                'username': folder_obj.user.username,
                'full_name': creator_name,
                'department': creator_department,
                'user_level': getattr(folder_obj.user.signup_details, 'user_level', 1) if hasattr(folder_obj.user, 'signup_details') else 1,
            }

        # Add creator metadata to folders
        for folder in filtered_folders:
            creator_info = folder_id_to_creator_info.get(folder['id'], {})
            folder['creator_username'] = creator_info.get('username', "Unknown User")
            folder['creator_full_name'] = creator_info.get('full_name', "Unknown User")
            folder['creator_department'] = creator_info.get('department', "Not specified")
            folder['creator_level'] = creator_info.get('user_level', 1)

        # Fetch files from Google Drive
        file_results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false",
            pageSize=100,
            fields="files(id, name, mimeType, size, createdTime, owners, webViewLink)"
        ).execute()

        all_drive_files = file_results.get('files', [])
        # Filter files based on access rights
        drive_files = [file for file in all_drive_files if file['id'] in accessible_file_ids]
        
        # Get uploader information from database with signup details
        file_id_to_uploader_info = {}
        file_id_to_level = {}
        for file_obj in accessible_files:
            try:
                signup_details = file_obj.user.signup_details
                uploader_name = f"{signup_details.first_name} {signup_details.last_name}"
            except SignupDetails.DoesNotExist:
                uploader_name = file_obj.user.username  # Fallback to username
            
            file_id_to_uploader_info[file_obj.file_id] = {
                'username': file_obj.user.username,
                'full_name': uploader_name,
                'department': getattr(file_obj.user.signup_details, 'department', 'Not specified') if hasattr(file_obj.user, 'signup_details') else 'Not specified'
            }
            file_id_to_level[file_obj.file_id] = file_obj.uploader_user_level

        # Add metadata for each file
        for file in drive_files:
            file['file_id'] = file['id']
            file['owner'] = file.get('owners', [{}])[0].get('displayName', 'Unknown')
            
            uploader_info = file_id_to_uploader_info.get(file['id'], {})
            file['uploader_username'] = uploader_info.get('username', "Unknown User")
            file['uploader_full_name'] = uploader_info.get('full_name', "Unknown User")
            file['uploader_department'] = uploader_info.get('department', "Not specified")
            file['uploader_level'] = file_id_to_level.get(file['id'], 1)
            
            file['date'] = datetime.fromisoformat(file['createdTime'][:-1]).strftime('%Y-%m-%d %H:%M:%S')
            file['size'] = f"{int(file.get('size', 0)) / 1024:.2f} KB" if 'size' in file else 'Unknown'
            file['icon'] = get_file_icon(file.get('mimeType', ''))
            file['webViewLink'] = file.get('webViewLink', '')

        # Fetch trashed files (apply same filtering)
        trashed_results = service.files().list(
            q="trashed = true",
            pageSize=20,
            fields="files(id, name, mimeType, size, createdTime, owners, webViewLink)"
        ).execute()

        all_trash_files = trashed_results.get('files', [])
        trash_files = [file for file in all_trash_files if file['id'] in accessible_file_ids]

        # Add metadata for each trashed file
        for file in trash_files:
            file['file_id'] = file['id']
            file['owner'] = file.get('owners', [{}])[0].get('displayName', 'Unknown')
            
            uploader_info = file_id_to_uploader_info.get(file['id'], {})
            file['uploader_username'] = uploader_info.get('username', "Unknown User")
            file['uploader_full_name'] = uploader_info.get('full_name', "Unknown User")
            file['uploader_department'] = uploader_info.get('department', "Not specified")
            file['uploader_level'] = file_id_to_level.get(file['id'], 1)
            
            file['date'] = datetime.fromisoformat(file['createdTime'][:-1]).strftime('%Y-%m-%d %H:%M:%S')
            file['size'] = f"{int(file.get('size', 0)) / 1024:.2f} KB" if 'size' in file else 'Unknown'
            file['icon'] = get_file_icon(file.get('mimeType', ''))
            file['webViewLink'] = file.get('webViewLink', '')

    except Exception as e:
        print("Error fetching files or folders from Google Drive:", str(e))
        messages.error(request, "Failed to fetch files or folders from Google Drive.")
        filtered_folders = []
        drive_files = []
        trash_files = []

    return render(request, 'core/saved.html', {
        'folders': filtered_folders,  # Now includes creator information
        'files': drive_files,
        'trash': trash_files,
        'ROOT_FOLDER_ID': ROOT_FOLDER_ID,
        'user_filter': user_name,
        'current_user_level': getattr(request.user.signup_details, 'user_level', 1) if hasattr(request.user, 'signup_details') else 1,
    })

def email(request):
    online_users = User.objects.all() 
    emails = Email.objects.all()

    return render(request, 'core/email.html', {
        'online_users': online_users,
        'emails': emails,
    })



def google_drive_auth(request):

    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to authorize Google Drive.")
        return redirect('core:login')

    creds_data = request.session.get('credentials')
    if creds_data:
        creds = Credentials(**creds_data)
        if creds.valid:
            messages.success(request, "Google Drive is already authorized.")
            return redirect('core:saved')

    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri='http://127.0.0.1:8000/drive/callback'
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    request.session['state'] = state
    return redirect(authorization_url)

def google_drive_callback(request):
    state = request.session['state']
    flow = Flow.from_client_secrets_file(
        settings.GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri='http://127.0.0.1:8000/drive/callback'
    )
    flow.fetch_token(authorization_response=request.build_absolute_uri())

    credentials = flow.credentials

    request.session['credentials'] = credentials_to_dict(credentials)

    return redirect('core:saved')



def upload_file_to_drive(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must be logged in to upload files.")
            return redirect('core:login')
            
        try:
            uploaded_files = request.FILES.getlist('file')
            folder_id = request.POST.get('folder_id', ROOT_FOLDER_ID)
            
            creds_data = request.session.get('credentials')
            if not creds_data:
                messages.error(request, "You need to authorize Google Drive access first.")
                return redirect('core:google_drive_auth')
            
            creds = Credentials(**creds_data)
            service = build('drive', 'v3', credentials=creds)
            
            # Get current user's level and department
            try:
                signup_details = request.user.signup_details
                user_level = signup_details.user_level
                user_department = signup_details.department
            except SignupDetails.DoesNotExist:
                user_level = 1  # Default to lowest level
                user_department = "Not specified"
            
            for uploaded_file in uploaded_files:
                # Google Drive upload code
                file_metadata = {
                    'name': uploaded_file.name,
                    'parents': [folder_id]
                }
                
                media = MediaIoBaseUpload(
                    BytesIO(uploaded_file.read()),
                    mimetype=uploaded_file.content_type,
                    resumable=True
                )
                
                file = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
                
                # Create DriveFile with user level information
                DriveFile.objects.create(
                    user=request.user,
                    name=uploaded_file.name,
                    file_id=file.get('id'),
                    uploader_user_level=user_level,
                    uploader_department=user_department
                )
            
            if folder_id == ROOT_FOLDER_ID:
                return redirect('core:saved')
            else:
                return redirect('core:view_folder_contents', folder_id=folder_id)

        except Exception as e:
            print("Drive upload failed:", str(e))
            return HttpResponse(f"Error: {e}", status=500)

    return HttpResponse("Invalid method", status=405)   

def delete_files_from_drive(request):
    if request.method == 'POST':
        file_ids = request.POST.getlist('file_ids[]')  # Get the list of file IDs to delete
        folder_id = request.POST.get('folder_id', ROOT_FOLDER_ID)  # Get the folder ID from the form, default to root folder

        creds_data = request.session.get('credentials')
        if not creds_data:
            return JsonResponse({'error': 'You must authorize Google Drive to delete files.'}, status=403)

        creds = Credentials(**creds_data)

        try:
            service = build('drive', 'v3', credentials=creds)

            for file_id in file_ids:
                service.files().delete(fileId=file_id).execute()

            return JsonResponse({'success': True, 'message': 'Files deleted successfully.', 'folder_id': folder_id})

        except Exception as e:
            print("Error deleting files from Google Drive:", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def create_folder_in_drive(request):
    if request.method == 'POST':
        folder_name = request.POST.get('folder_name')
        parent_folder_id = request.POST.get('parent_folder_id', ROOT_FOLDER_ID)

        creds_data = request.session.get('credentials')
        if not creds_data:
            messages.error(request, "You must authorize Google Drive to create folders.")
            return redirect('core:google_drive_auth')

        creds = Credentials(**creds_data)

        try:
            service = build('drive', 'v3', credentials=creds)

            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [parent_folder_id]
            }

            folder = service.files().create(
                body=folder_metadata,
                fields='id, name'
            ).execute()

            # Get current user's level and department
            try:
                signup_details = request.user.signup_details
                user_level = signup_details.user_level
                user_department = signup_details.department
            except SignupDetails.DoesNotExist:
                user_level = 1
                user_department = "Not specified"

            # Save folder with user level information
            DriveFolder.objects.create(
                user=request.user,
                name=folder['name'],
                folder_id=folder['id'],
                parent_folder_id=parent_folder_id,
                creator_user_level=user_level,
                creator_department=user_department
            )

            messages.success(request, f"Folder '{folder['name']}' created successfully.")
            
            if parent_folder_id == ROOT_FOLDER_ID:
                return redirect('core:saved')
            else:
                return redirect('core:view_folder_contents', folder_id=parent_folder_id)

        except Exception as e:
            print("Error creating folder in Google Drive:", str(e))
            messages.error(request, f"Error creating folder: {str(e)}")
            return redirect('core:saved')

    return redirect('core:saved')

def delete_folders(request):
    if request.method == 'POST':
        folder_ids = request.POST.getlist('folder_ids[]')
        
        creds_data = request.session.get('credentials')
        if not creds_data:
            return JsonResponse({'error': 'You must authorize Google Drive to delete folders.'}, status=403)
            
        creds = Credentials(**creds_data)
        
        try:
            service = build('drive', 'v3', credentials=creds)
            
            deleted_count = 0
            for folder_id in folder_ids:
                service.files().delete(fileId=folder_id).execute()
                deleted_count += 1
                
            return JsonResponse({
                'success': True, 
                'message': f'{deleted_count} folder(s) deleted successfully.'
            })
            
        except Exception as e:
            print("Error deleting folders from Google Drive:", str(e))
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def view_folder_contents(request, folder_id):
    creds_data = request.session.get('credentials')
    if not creds_data:
        messages.error(request, "You must authorize Google Drive to view folder contents.")
        return redirect('core:google_drive_auth')

    # Check if user has access to this specific folder
    accessible_files, accessible_folders = get_accessible_files_for_user(request.user)
    accessible_folder_ids = set(accessible_folders.values_list('folder_id', flat=True))
    
    # If the folder_id is not in accessible folders and it's not the root folder, deny access
    if folder_id != ROOT_FOLDER_ID and folder_id not in accessible_folder_ids:
        messages.error(request, "You don't have permission to access this folder.")
        return redirect('core:saved')

    creds = Credentials(**creds_data)

    try:
        service = build('drive', 'v3', credentials=creds)

        # Get file IDs and folder IDs that user can access
        accessible_file_ids = set(accessible_files.values_list('file_id', flat=True))

        # Fetch folders from the root folder
        folder_results = service.files().list(
            q=f"'{ROOT_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
            pageSize=100,
            fields="files(id, name, parents)"
        ).execute()

        all_folders = folder_results.get('files', [])
        # Filter folders based on access rights
        filtered_folders = [folder for folder in all_folders if folder['id'] in accessible_folder_ids]

        # Get creator information from database with signup details for folders
        folder_id_to_creator_info = {}
        for folder_obj in accessible_folders:
            try:
                signup_details = folder_obj.user.signup_details
                creator_name = f"{signup_details.first_name} {signup_details.last_name}"
                creator_department = signup_details.department
            except SignupDetails.DoesNotExist:
                creator_name = folder_obj.user.username  # Fallback to username
                creator_department = "Not specified"
            
            folder_id_to_creator_info[folder_obj.folder_id] = {
                'username': folder_obj.user.username,
                'full_name': creator_name,
                'department': creator_department,
                'user_level': getattr(folder_obj.user.signup_details, 'user_level', 1) if hasattr(folder_obj.user, 'signup_details') else 1,
            }

        # Add creator metadata to folders
        for folder in filtered_folders:
            creator_info = folder_id_to_creator_info.get(folder['id'], {})
            folder['creator_username'] = creator_info.get('username', "Unknown User")
            folder['creator_full_name'] = creator_info.get('full_name', "Unknown User")
            folder['creator_department'] = creator_info.get('department', "Not specified")
            folder['creator_level'] = creator_info.get('user_level', 1)

        # Rest of your existing file processing code...
        file_results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false",
            pageSize=100,
            fields="files(id, name, mimeType, size, createdTime, owners, webViewLink)"
        ).execute()

        all_drive_files = file_results.get('files', [])
        drive_files = [file for file in all_drive_files if file['id'] in accessible_file_ids]

        # Get uploader information from database with signup details
        file_id_to_uploader_info = {}
        file_id_to_level = {}
        for file_obj in accessible_files:
            try:
                signup_details = file_obj.user.signup_details
                uploader_name = f"{signup_details.first_name} {signup_details.last_name}"
            except SignupDetails.DoesNotExist:
                uploader_name = file_obj.user.username  # Fallback to username
            
            file_id_to_uploader_info[file_obj.file_id] = {
                'username': file_obj.user.username,
                'full_name': uploader_name,
                'department': getattr(file_obj.user.signup_details, 'department', 'Not specified') if hasattr(file_obj.user, 'signup_details') else 'Not specified'
            }
            file_id_to_level[file_obj.file_id] = file_obj.uploader_user_level

        # Add metadata for files including uploader
        for file in drive_files:
            file['file_id'] = file['id']
            file['owner'] = file.get('owners', [{}])[0].get('displayName', 'Unknown')
            
            uploader_info = file_id_to_uploader_info.get(file['id'], {})
            file['uploader_username'] = uploader_info.get('username', "Unknown User")
            file['uploader_full_name'] = uploader_info.get('full_name', "Unknown User")
            file['uploader_department'] = uploader_info.get('department', "Not specified")
            file['uploader_level'] = file_id_to_level.get(file['id'], 1)
            
            file['date'] = datetime.fromisoformat(file['createdTime'][:-1]).strftime('%Y-%m-%d %H:%M:%S')
            file['size'] = f"{int(file.get('size', 0)) / 1024:.2f} KB" if 'size' in file else 'Unknown'
            file['icon'] = get_file_icon(file.get('mimeType', ''))
            file['webViewLink'] = file.get('webViewLink', '')

    except Exception as e:
        print("Error fetching folder contents from Google Drive:", str(e))
        messages.error(request, "Failed to fetch folder contents from Google Drive.")
        filtered_folders = []
        drive_files = []

    return render(request, 'core/saved.html', {
        'folders': filtered_folders,  # Now includes creator information
        'files': drive_files,
        'folder_id': folder_id,
        'ROOT_FOLDER_ID': ROOT_FOLDER_ID,
        'current_user_level': getattr(request.user.signup_details, 'user_level', 1) if hasattr(request.user, 'signup_details') else 1,
    })

def get_accessible_files_for_user(user):
    """
    Get files that a user can access based on their level and department
    Higher levels can see lower level files, but only within their department (except executives)
    """
    try:
        user_signup_details = user.signup_details
        user_level = user_signup_details.user_level
        user_department = user_signup_details.department
    except SignupDetails.DoesNotExist:
        user_level = 1
        user_department = "Not specified"
    
    # Executive Position (Level 4) can see all files from all departments
    if user_level == 4:
        accessible_files = DriveFile.objects.all()
        accessible_folders = DriveFolder.objects.all()
    # Dept. Manager (Level 3) can see level 1, 2, and 3 files from their department only
    elif user_level == 3:
        accessible_files = DriveFile.objects.filter(
            uploader_user_level__lte=3,
            uploader_department=user_department
        )
        accessible_folders = DriveFolder.objects.filter(
            creator_user_level__lte=3,
            creator_department=user_department
        )
    # Supervisor (Level 2) can see level 1 and 2 files from their department only
    elif user_level == 2:
        accessible_files = DriveFile.objects.filter(
            uploader_user_level__lte=2,
            uploader_department=user_department
        )
        accessible_folders = DriveFolder.objects.filter(
            creator_user_level__lte=2,
            creator_department=user_department
        )
    # Employee (Level 1) can only see their own files
    else:
        accessible_files = DriveFile.objects.filter(user=user)
        accessible_folders = DriveFolder.objects.filter(user=user)
    
    return accessible_files, accessible_folders

def get_accessible_files_for_user_with_department_filter(user, include_department_filter=True):
    """
    Enhanced version with department filtering enabled by default
    """
    try:
        user_signup_details = user.signup_details
        user_level = user_signup_details.user_level
        user_department = user_signup_details.department
    except SignupDetails.DoesNotExist:
        user_level = 1
        user_department = "Not specified"
    
    # Executive Position (Level 4) - can see all files from all departments
    if user_level == 4:
        accessible_files = DriveFile.objects.all()
        accessible_folders = DriveFolder.objects.all()
    # Dept. Manager (Level 3) - can see their department files + lower levels in their department
    elif user_level == 3:
        if include_department_filter:
            accessible_files = DriveFile.objects.filter(
                uploader_user_level__lte=3,
                uploader_department=user_department
            )
            accessible_folders = DriveFolder.objects.filter(
                creator_user_level__lte=3,
                creator_department=user_department
            )
        else:
            # Fallback without department filter
            accessible_files = DriveFile.objects.filter(uploader_user_level__lte=3)
            accessible_folders = DriveFolder.objects.filter(creator_user_level__lte=3)
    # Supervisor (Level 2) - can see level 1 and 2 files in their department
    elif user_level == 2:
        if include_department_filter:
            accessible_files = DriveFile.objects.filter(
                uploader_user_level__lte=2,
                uploader_department=user_department
            )
            accessible_folders = DriveFolder.objects.filter(
                creator_user_level__lte=2,
                creator_department=user_department
            )
        else:
            accessible_files = DriveFile.objects.filter(uploader_user_level__lte=2)
            accessible_folders = DriveFolder.objects.filter(creator_user_level__lte=2)
    # Employee (Level 1) - can only see their own files
    else:
        accessible_files = DriveFile.objects.filter(user=user)
        accessible_folders = DriveFolder.objects.filter(user=user)
    
    return accessible_files, accessible_folders


def move_files_to_trash(request):
    if request.method == 'POST':
        file_ids = request.POST.getlist('file_ids[]')
        folder_id = request.POST.get('folder_id', ROOT_FOLDER_ID)

        creds_data = request.session.get('credentials')
        if not creds_data:
            return JsonResponse({'error': 'You must authorize Google Drive to manage files.'}, status=403)

        creds = Credentials(**creds_data)
        
        try:
            service = build('drive', 'v3', credentials=creds)
            
            # Get current user's email for ownership comparison
            user_info = service.about().get(fields="user").execute()
            current_user_email = user_info['user']['emailAddress']
            
            trashed_files = []
            deleted_files = []
            skipped_files = []
            
            for file_id in file_ids:
                try:
                    # Get file info with owner information
                    file_info = service.files().get(
                        fileId=file_id, 
                        fields="name,owners"
                    ).execute()
                    
                    file_name = file_info.get("name", "Unknown")
                    file_owners = file_info.get("owners", [])
                    
                    # Check if current user is the owner
                    is_owner = any(owner.get('emailAddress') == current_user_email for owner in file_owners)
                    
                    if is_owner:
                        # If owner, move to trash
                        service.files().update(
                            fileId=file_id,
                            body={'trashed': True}
                        ).execute()
                        trashed_files.append({"id": file_id, "name": file_name})
                    else:
                        # If not owner, permanently delete
                        service.files().delete(fileId=file_id).execute()
                        deleted_files.append({"id": file_id, "name": file_name})
                    
                except HttpError as e:
                    if e.resp.status == 403:
                        # Permission error
                        skipped_files.append({"id": file_id, "name": file_name})
                        continue
                    else:
                        # Re-raise other errors
                        raise
            
            # Create appropriate response message
            message_parts = []
            if trashed_files:
                message_parts.append(f"Moved {len(trashed_files)} of your file(s) to trash")
            if deleted_files:
                message_parts.append(f"Permanently deleted {len(deleted_files)} file(s) owned by others")
            if skipped_files:
                message_parts.append(f"Skipped {len(skipped_files)} file(s) due to insufficient permissions")
            
            message = ". ".join(message_parts)
            success = bool(trashed_files or deleted_files)
            is_root_folder = (folder_id == ROOT_FOLDER_ID)
            
            return JsonResponse({
                'success': success,
                'message': message,
                'folder_id': folder_id,
                'is_root_folder': is_root_folder,
                'trashed_files': trashed_files,
                'deleted_files': deleted_files,
                'skipped_files': skipped_files
            })

        except Exception as e:
            print("Error processing files:", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def get_trashed_files(request):
    creds_data = request.session.get('credentials')
    if not creds_data:
        return []

    creds = Credentials(**creds_data)

    try:
        service = build('drive', 'v3', credentials=creds)
        
        # Fetch trashed files
        trashed_results = service.files().list(
            q="trashed = true",
            pageSize=20,
            fields="files(id, name, mimeType, webViewLink)"
        ).execute()

        return trashed_results.get('files', [])

    except Exception as e:
        print("Error fetching trashed files:", str(e))
        return []
    


def empty_trash(request):
    if request.method == 'POST':
        creds_data = request.session.get('credentials')
        if not creds_data:
            return JsonResponse({'error': 'You must authorize Google Drive to empty trash.'}, status=403)

        creds = Credentials(**creds_data)

        try:
            service = build('drive', 'v3', credentials=creds)
            
            # Empty trash (deletes all trashed files permanently)
            service.files().emptyTrash().execute()
            
            messages.success(request, "Trash emptied successfully.")
            return redirect('core:saved')

        except Exception as e:
            print("Error emptying trash:", str(e))
            messages.error(request, f"Error emptying trash: {str(e)}")
            return redirect('core:saved')

    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def restore_from_trash(request):
    if request.method == 'POST':
        creds_data = request.session.get('credentials')
        if not creds_data:
            return redirect('core:google_drive_auth')

        creds = Credentials(**creds_data)

        try:
            service = build('drive', 'v3', credentials=creds)
            
            # Get files in trash
            results = service.files().list(
                q="trashed=true",
                fields="files(id, name)"
            ).execute()
            
            trashed_files = results.get('files', [])
            
            # Restore each file
            restored_count = 0
            for file in trashed_files:
                service.files().update(
                    fileId=file['id'],
                    body={'trashed': False}
                ).execute()
                restored_count += 1
                
            messages.success(request, f"Successfully restored {restored_count} files from trash")
            return redirect('core:saved')
            
        except Exception as e:
            messages.error(request, f"Error restoring files: {str(e)}")
            return redirect('core:saved')
            
    return redirect('core:saved')

def credentials_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
    
# For notification sidebar Popup TEST
def get_notifications(request):
    notifications = Notification.objects.all().order_by('-created_at')[:10]  # Fetch the latest 10 notifications
    data = [
        {
            "title": notification.title,
            "description": notification.description,
            "posted_by": notification.posted_by,
            "created_at": notification.created_at.strftime("%b %d, %Y"),
        }
        for notification in notifications
    ]
    return JsonResponse(data, safe=False)

def get_file_icon(mime_type):
    file_icons = {
        'application/pdf': 'Images/pdf.png',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Images/docx.png',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Images/csv.png',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'Images/pptx.png',
        'image/jpeg': 'Images/image.png',
        'image/png': 'Images/image.png',
        'text/plain': 'Images/default.png',
        # Add more MIME types as needed
    }
    return file_icons.get(mime_type, 'Images/default.png')


@login_required
def get_all_users_for_usermap(request):
    users_data = []
    
    # Only get users who have completed signup details
    signup_details = SignupDetails.objects.select_related('user').all()
    
    for detail in signup_details:
        user = detail.user
        
        # Add users to the response with their signup details
        users_data.append({
            'id': user.id,
            'first_name': detail.first_name,
            'last_name': detail.last_name,
            'department': detail.department or "Not specified",
            'position': detail.position or "Not specified",
            'user_level': detail.user_level,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            'x': 100 + ((user.id * 200) % 800),  # Initial positions
            'y': 100 + ((user.id * 150) // 800) * 150
        })
    
    return JsonResponse(users_data, safe=False)

# Helper function to determine file type letter
def get_file_type_letter(mime_type):
    if 'presentation' in mime_type:
        return 'P'
    elif 'spreadsheet' in mime_type:
        return 'S'
    elif 'document' in mime_type:
        return 'D'
    elif 'image' in mime_type:
        return 'I'
    elif 'pdf' in mime_type:
        return 'P'
    else:
        return 'F'  # Generic file

def load_user_map(request):
    """Load saved user map arrangement"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=403)
    
    # This is a simple implementation - you might want to store this in a database
    # For now, we'll return an empty response which will fall back to localStorage
    return JsonResponse({
        'users': [],
        'connections': []
    })

@login_required
@require_POST
def delete_user(request):
    # Check if user has admin privileges
    if not request.user.is_staff and not request.user.is_superuser:
        return JsonResponse({
            'success': False,
            'error': 'You do not have permission to delete users.'
        })
    
    user_id = request.POST.get('user_id')
    
    if not user_id:
        return JsonResponse({
            'success': False,
            'error': 'No user ID provided.'
        })
    
    try:
        user_to_delete = User.objects.get(id=user_id)
        
        # Don't allow deleting yourself
        if user_to_delete == request.user:
            return JsonResponse({
                'success': False,
                'error': 'You cannot delete your own account.'
            })
            
        was_active = user_to_delete.is_active
        username = user_to_delete.username
        
        # Delete user
        user_to_delete.delete()
        
        # Log the deletion
       
        username = user_to_delete.username
        
        # Delete user
        user_to_delete.delete()
        
        # Log the deletion
        print(f"User {username} (ID: {user_id}) deleted by {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'was_active': was_active,
            'message': f'User {username} deleted successfully.'
        })
    except User.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'User not found.'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def get_project_folder(request, project_id):
    try:
        # Get current user's full name
        try:
            user_signup_details = request.user.signup_details
            user_full_name = f"{user_signup_details.first_name} {user_signup_details.last_name}"
        except SignupDetails.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'User profile not complete. Please complete your profile first.'
            })
        
        project = Project.objects.get(id=project_id)
        
        # Check if user is project manager or team member
        is_project_manager = project.project_manager == user_full_name
        is_team_member = ProjectMember.objects.filter(
            project=project,
            member_name=user_full_name
        ).exists()
        
        if not (is_project_manager or is_team_member):
            return JsonResponse({
                'success': False,
                'error': 'Access denied: You are not part of this project team.'
            })
        
        # Find the associated drive folder
        try:
            drive_folder = DriveFolder.objects.get(name=project.name)
            folder_url = f"https://drive.google.com/drive/folders/{drive_folder.folder_id}"
            
            return JsonResponse({
                'success': True,
                'folder_url': folder_url,
                'folder_name': drive_folder.name
            })
        except DriveFolder.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Project folder not found in Drive. The folder may not have been created yet.'
            })
            
    except Project.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Project not found'
        })
    except Exception as e:
        print(f"Error in get_project_folder: {str(e)}")  # Debug log
        return JsonResponse({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })
