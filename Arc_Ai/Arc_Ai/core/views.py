from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from .models import Notification

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

GOOGLE_CLIENT_SECRETS_FILE = os.path.join(settings.BASE_DIR, 'secret', 'client_secret.json')

SCOPES = ['https://www.googleapis.com/auth/drive.file']

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

def edit_user(request):
    return render(request, 'core/edit_user.html')

def signup_details(request):

    if request.method == 'POST':
        profile_avatar = request.FILES.get('profile_avatar')
        first_name = request.POST.get('first_name')
        middle_name = request.POST.get('middle_name')
        last_name = request.POST.get('last_name')
        complete_address = request.POST.get('complete_address')
        contact_number = request.POST.get('contact_number')
        gender = request.POST.get('gender')

        signup_details = SignupDetails.objects.create(
            profile_avatar=profile_avatar,
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            complete_address=complete_address,
            contact_number=contact_number,
            gender=gender
        )

        PersonalInformation.objects.create(
            signup_details=signup_details,
            name=f"{first_name} {last_name}",
            email=request.POST.get('email'),
            complete_address=complete_address,
            contact_number=contact_number,
            age=request.POST.get('age'),
            birth_date=request.POST.get('birth_date', None),
            gender=gender,
            user_title=request.POST.get('user_title')
        )

        signup_details.save()

        messages.info(request, "Profile details saved successfully!")
        return redirect('core:home')

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

def landingpage(request):
    return render(request, 'core/landingpage.html')

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

def landingpage(request):
    return render(request, 'core/landingpage.html')

def saved(request):
    folders = [f"Folder {i}" for i in range(1, 21)]
    trash = [f"Trash File {i}" for i in range(1, 21)]

    creds_data = request.session.get('credentials')
    if not creds_data:
        messages.error(request, "You must authorize Google Drive to fetch files.")
        return redirect('core:google_drive_auth')

    creds = Credentials(**creds_data)

    try:
        service = build('drive', 'v3', credentials=creds)

        results = service.files().list(
            pageSize=50,
            fields="files(id, name, mimeType, webViewLink, parents)"
        ).execute()

        drive_files = results.get('files', [])

    except Exception as e:
        print("Error fetching files from Google Drive:", str(e))
        messages.error(request, "Failed to fetch files from Google Drive.")
        drive_files = []

    return render(request, 'core/saved.html', {
        'folders': folders,
        'files': drive_files,
        'trash': trash,
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
        uploaded_file = request.FILES.get('file')
        print("Received file:", uploaded_file.name)

        creds_data = request.session.get('credentials')
        if not creds_data:
            print("No credentials in session. Redirecting to auth.")
            return redirect('core:google_drive_auth')

        creds = Credentials(**creds_data)

        try:
            service = build('drive', 'v3', credentials=creds)
            media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.content_type)
            file_metadata = {'name': uploaded_file.name,
                            'parents': ['1katYIAY6Xzw1fOorjULbdMAneODhdVpl']}

            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name'
            ).execute()

            DriveFile.objects.create(name=file['name'], file_id=file['id'])

            print(f"Uploaded to Drive: {file['name']} (ID: {file['id']})")

            return redirect('core:saved')

        except Exception as e:
            print("Drive upload failed:", str(e))
            return HttpResponse(f"Error: {e}", status=500)

    return HttpResponse("Invalid method", status=405)

def delete_files_from_drive(request):
    if request.method == 'POST':
        file_ids = request.POST.getlist('file_ids[]')

        creds_data = request.session.get('credentials')
        if not creds_data:
            return JsonResponse({'error': 'You must authorize Google Drive to delete files.'}, status=403)

        creds = Credentials(**creds_data)

        try:
            service = build('drive', 'v3', credentials=creds)

            for file_id in file_ids:
                service.files().delete(fileId=file_id).execute()

            return JsonResponse({'success': True, 'message': 'Files deleted successfully.'})

        except Exception as e:
            print("Error deleting files from Google Drive:", str(e))
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

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
