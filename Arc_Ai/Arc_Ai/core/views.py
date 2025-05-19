from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from .models import Notification
from django.utils.timezone import datetime
from django.contrib.auth import logout

# MODELS
from .models import Email, Project, PersonalInformation, EmployeeAward, DriveFile, SignupDetails
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

GOOGLE_CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'secret', 'client_secret.json')

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file"
]

ROOT_FOLDER_ID = '1wdS3rmcuuiZ-mr2aH7SfYSTAF6Uvlv5z'

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
# This is for local development only. In production, use HTTPS.

#[PRACTICE TEMPLATES] ====================================================================
from .models import UserProfile

def practice(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')

        if UserProfile.objects.filter(email=email).exists():
            return render(request, 'core/practice.html', {
                'error': 'Email already exists. Please use a different email.'
            })

        UserProfile.objects.create(
            email=email,
            address=address,
            password=password
        )

        # Store email and address in session
        request.session['current_email'] = email
        request.session['current_address'] = address

        return redirect('core:practice1')  # redirect after POST (best practice)

    return render(request, 'core/practice.html')

from .models import EditProfile

def practice1(request):
    # Get defaults from session
    current_email = request.session.get('current_email', '')
    current_address = request.session.get('current_address', '')

    if request.method == 'POST':
        # Use session values if not provided in POST (for first load, use session)
        current_email = request.POST.get('current_email', current_email)
        new_email = request.POST.get('new_email')
        current_address = request.POST.get('current_address', current_address)
        new_address = request.POST.get('new_address')

        if not (current_email and new_email and current_address and new_address):
            return render(request, 'core/practice1.html', {
                'error': 'All fields are required.',
                'current_email': current_email,
                'current_address': current_address
            })

        if UserProfile.objects.filter(email=new_email).exclude(email=current_email).exists():
            return render(request, 'core/practice1.html', {
                'error': 'New email already exists.',
                'current_email': current_email,
                'current_address': current_address
            })

        try:
            user = UserProfile.objects.get(email=current_email, address=current_address)
            EditProfile.objects.update_or_create(
                user=user,
                defaults={'new_email': new_email, 'new_address': new_address}
            )
            user.email = new_email
            user.address = new_address
            user.save()
            # Update session to new values
            request.session['current_email'] = new_email
            request.session['current_address'] = new_address
            return render(request, 'core/practice1.html', {
                'success': 'Email and Address updated!',
                'current_email': new_email,
                'current_address': new_address
            })
        except UserProfile.DoesNotExist:
            return render(request, 'core/practice1.html', {
                'error': 'User not found.',
                'current_email': current_email,
                'current_address': current_address
            })

    return render(request, 'core/practice1.html', {
        'current_email': current_email,
        'current_address': current_address
    })

#[PRACTICE TEMPLATES] ====================================================================\

def admin_create_project_details(request):
    return render(request, 'core/admin_create_project_details.html')

def user_involved_map(request):
    return render(request, 'core/user_involved_map.html')

def edit_user_profile(request):
    return render(request, 'core/edit_user_profile.html')

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
    
    # Get all users
    users = User.objects.all().order_by('username')
    
    # Count active users
    active_users = User.objects.filter(is_active=True).count()
    
    return render(request, 'core/admin_users_page.html', {
        'users': users,
        'total_users': users.count(),
        'active_users': active_users,
    })
    
def admin_edit_project_details(request):
    return render(request, 'core/admin_edit_project_details.html')

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

def create_project(request):
    if request.method == 'POST':
        # ... get other fields ...
        name = request.POST.get('name')
        project_id = request.POSt.get('project_id')
        start_date = request.POST.get('start_date')
        finish_date = request.POST.get('finish_date')
        project_status = request.POST.get('project_status')
        project_manager = request.POST.get('project_manager')

        project = Project.objects.create(
            name=name,
            project_id=project_id,
            start_date=start_date,
            finish_date=finish_date,
            project_status=project_status,
            project_manager=project_manager
        )
        return redirect('core:admin_project_page')
    return render(request, 'core/create_project.html')

# =================================== FOR CREATION OF PROJECTS ===================================



def admin_files_page(request):
    return render(request, 'core/admin_files_page.html')

def signup_details(request):
    if request.method == 'POST':
        profile_avatar = request.FILES.get('profile_avatar')
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        complete_address = request.POST.get('complete_address')
        contact_number = request.POST.get('contact_number')
        gender = request.POST.get('gender')

        # Create SignupDetails instance
        signup_details = SignupDetails.objects.create(
            profile_avatar=profile_avatar,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            complete_address=complete_address,
            contact_number=contact_number,
            gender=gender
        )

        messages.info(request, "Profile details saved successfully!")
        return redirect('core:home')

    return render(request, 'core/signup_details.html', {
        'range': range(1, 16)  # Pass numbers 1 to 15 to the template
    })



def profilepage(request):
    projects = Project.objects.all()
    employee_awards = EmployeeAward.objects.all()
    personal_information = PersonalInformation.objects.first()

    return render(request, 'core/profilepage.html', {
        'projects': projects,
        'personal_information': personal_information,
        'employee_awards': employee_awards,
    })

def landingpage(request):
    return render(request, 'core/landingpage.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('core:login')

def login(request):
    if request.user.is_authenticated:
        return redirect('core:home')  # Already logged in, go to home
        
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
                response = redirect('core:home')
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

def home(request):
    return render(request, 'core/home.html')

def organization(request):
    projects = Project.objects.all().order_by('-project_id')  # or your preferred ordering
    personal_information = PersonalInformation.objects.first()
    employee_awards = EmployeeAward.objects.all()
    top_project = projects.first() if projects else None

    return render(request, 'core/organization.html', {
        'projects': projects,
        'top_project': top_project,
        'personal_information': personal_information,
        'employee_awards': employee_awards,
    })

def landingpage(request):
    return render(request, 'core/landingpage.html')

def saved(request):
    folder_id = ROOT_FOLDER_ID
    
    creds_data = request.session.get('credentials')
    if not creds_data:
        messages.error(request, "You must authorize Google Drive to fetch files.")
        return redirect('core:google_drive_auth')

    creds = Credentials(**creds_data)

    try:
        service = build('drive', 'v3', credentials=creds)

        # Fetch folders from the root folder
        folder_results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false",
            pageSize=100,
            fields="files(id, name, parents)"
        ).execute()

        folders = folder_results.get('files', [])

        # Fetch files from the root folder
        file_results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false",
            pageSize=100,
            fields="files(id, name, mimeType, size, createdTime, owners)"
        ).execute()

        drive_files = file_results.get('files', [])
        
        # Fetch trashed files
        trashed_results = service.files().list(
            q="trashed = true",
            pageSize=20,
            fields="files(id, name, mimeType, webViewLink)"
        ).execute()

        trash_files = trashed_results.get('files', [])
    # Add metadata for each file
        for file in drive_files:
            file['file_id'] = file['id']
            file['owner'] = file.get('owners', [{}])[0].get('displayName', 'Unknown')
            file['date'] = datetime.fromisoformat(file['createdTime'][:-1]).strftime('%Y-%m-%d %H:%M:%S')
            file['size'] = f"{int(file['size']) / 1024:.2f} KB" if 'size' in file else 'Unknown'
            file['icon'] = get_file_icon(file.get('mimeType', ''))

    except Exception as e:
        print("Error fetching files or folders from Google Drive:", str(e))
        messages.error(request, "Failed to fetch files or folders from Google Drive.")
        folders = []
        drive_files = []
        trash_files = []

    return render(request, 'core/saved.html', {
        'folders': folders,
        'files': drive_files,
        'trash': trash_files,  # Now passing actual trashed files
        'ROOT_FOLDER_ID': ROOT_FOLDER_ID,
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
        uploaded_files = request.FILES.getlist('file')  # Get all uploaded files
        folder_id = request.POST.get('folder_id', ROOT_FOLDER_ID)  # Get the folder ID from the form, default to root folder

        creds_data = request.session.get('credentials')
        if not creds_data:
            return redirect('core:google_drive_auth')

        creds = Credentials(**creds_data)

        try:
            service = build('drive', 'v3', credentials=creds)

            for uploaded_file in uploaded_files:
                media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.content_type)
                file_metadata = {
                    'name': uploaded_file.name,
                    'parents': [folder_id]  # Use the folder ID dynamically
                }

                file = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id, name'
                ).execute()

                # Save the file details in the database
                DriveFile.objects.create(name=file['name'], file_id=file['id'])

                print(f"Uploaded to Drive: {file['name']} (ID: {file['id']})")

            # Check if upload was to root folder
            if folder_id == ROOT_FOLDER_ID:
                return redirect('core:saved')  # Redirect to saved.html for root folder
            else:
                return redirect('core:view_folder_contents', folder_id=folder_id)  # Redirect to folder view for other folders

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
        folder_name = request.POST.get('folder_name')  # Get the folder name from the form

        creds_data = request.session.get('credentials')
        if not creds_data:
            messages.error(request, "You must authorize Google Drive to create folders.")
            return redirect('core:google_drive_auth')

        creds = Credentials(**creds_data)

        try:
            service = build('drive', 'v3', credentials=creds)

            # Define folder metadata
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [ROOT_FOLDER_ID]  # Use the root folder ID
            }

            # Create the folder
            folder = service.files().create(
                body=folder_metadata,
                fields='id, name'
            ).execute()

            print(f"Folder created: {folder['name']} (ID: {folder['id']})")
            messages.success(request, f"Folder '{folder['name']}' created successfully.")
            return redirect('core:saved')  # Redirect to the saved view

        except Exception as e:
            print("Error creating folder in Google Drive:", str(e))
            messages.error(request, f"Error creating folder: {str(e)}")
            return redirect('core:saved')  # Redirect to the saved view even on error

    messages.error(request, "Invalid request method.")
    return redirect('core:saved')  # Redirect to the saved view for invalid request methods


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

    creds = Credentials(**creds_data)

    try:
        service = build('drive', 'v3', credentials=creds)

        # Fetch folders from the root folder
        folder_results = service.files().list(
            q=f"'{ROOT_FOLDER_ID}' in parents and mimeType = 'application/vnd.google-apps.folder'",
            pageSize=100,
            fields="files(id, name, parents)"
        ).execute()

        folders = folder_results.get('files', [])

        # Fetch files inside the clicked folder
        file_results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder'",
            pageSize=100,
            fields="files(id, name, mimeType, webViewLink, parents)"
        ).execute()

        drive_files = file_results.get('files', [])
        
        # Fetch trashed files - ADD THIS BLOCK
        trashed_results = service.files().list(
            q="trashed = true",
            pageSize=20,
            fields="files(id, name, mimeType, webViewLink)"
        ).execute()

        trash_files = trashed_results.get('files', [])

        # Add this to your view_folder_contents function after fetching files
        for file in drive_files:
            file['file_id'] = file['id']
            # Add any other metadata processing you need
            file['icon'] = get_file_icon(file.get('mimeType', ''))

    except Exception as e:
        print("Error fetching folder contents from Google Drive:", str(e))
        messages.error(request, "Failed to fetch folder contents from Google Drive.")
        folders = []
        drive_files = []
        trash_files = []  # Add this line

    return render(request, 'core/saved.html', {
        'folders': folders,  # Pass folders to the template
        'files': drive_files,  # Pass files inside the clicked folder
        'folder_id': folder_id,  # Pass the current folder ID to the template
        'ROOT_FOLDER_ID': ROOT_FOLDER_ID,  # Pass ROOT_FOLDER_ID to the template
        'trash': trash_files,  # Add this line to pass trash files
    })


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