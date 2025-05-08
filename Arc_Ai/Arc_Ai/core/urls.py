from django.urls import path
from . import views
from django.urls import path
from . import views


app_name = 'core'

urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('landingpage/', views.landingpage, name='landingpage'),
    path('signup_details/', views.signup_details, name='signup_details'),
    path('landingpage/', views.landingpage, name='landingpage'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('saved/', views.saved, name='saved'),
    path('email/', views.email, name='email'),
    path('home/', views.home, name='home'),
    path('organization/', views.organization, name='organization'),
    path('profilepage/', views.profilepage, name='profilepage'),
    path('login/', views.login, name='login'),
    path('drive/auth/', views.google_drive_auth, name='google_drive_auth'),
    path('drive/callback/', views.google_drive_callback, name='google_drive_callback'),
    path('drive/upload/', views.upload_file_to_drive, name='upload_file_to_drive'),

    
]
