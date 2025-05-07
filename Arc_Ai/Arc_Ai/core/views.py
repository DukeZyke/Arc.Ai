from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from .models import Email, Project, PersonalInformation, EmployeeAward, DriveFile
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
    files = DriveFile.objects.all().order_by('-uploaded_at')      # 20 files
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



def google_drive_auth(request):
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

    # ✅ Get credentials from the flow object after fetching token
    credentials = flow.credentials

    # ✅ Store credentials in session
    request.session['credentials'] = credentials_to_dict(credentials)

    return redirect('core:saved')



def upload_file_to_drive(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        print("Received file:", uploaded_file.name)

        # Load credentials from session
        creds_data = request.session.get('credentials')
        if not creds_data:
            print("No credentials in session. Redirecting to auth.")
            return redirect('core:google_drive_auth')

        creds = Credentials(**creds_data)

        try:
            service = build('drive', 'v3', credentials=creds)

            # Convert uploaded file into a media upload
            media = MediaIoBaseUpload(uploaded_file, mimetype=uploaded_file.content_type)
            file_metadata = {'name': uploaded_file.name,
                             'parents': ['1katYIAY6Xzw1fOorjULbdMAneODhdVpl']}

            # Upload file to Google Drive
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

def credentials_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }
