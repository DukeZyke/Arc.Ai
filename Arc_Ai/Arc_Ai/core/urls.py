from django.urls import path
from . import views
from django.urls import path
from . import views


app_name = 'core'

urlpatterns = [
    path('', views.edit_user, name='edit_user'),
    path('edit_user', views.edit_user, name='edit_user'),
    path('signup_details/', views.signup_details, name='signup_details'),
    path('landingpage/', views.landingpage, name='landingpage'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('saved/', views.saved, name='saved'),
    path('email/', views.email, name='email'),
    path('home/', views.home, name='home'),
    path('organization/', views.organization, name='organization'),
    path('profilepage/', views.profilepage, name='profilepage'),
    path('drive/auth/', views.google_drive_auth, name='google_drive_auth'),
    path('drive/callback/', views.google_drive_callback, name='google_drive_callback'),
    path('drive/upload/', views.upload_file_to_drive, name='upload_file_to_drive'),
    path('delete_files_from_drive/', views.delete_files_from_drive, name='delete_files_from_drive'),  
    path('api/notifications/', views.get_notifications, name='get_notifications'),
]
