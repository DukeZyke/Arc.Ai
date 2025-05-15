from django.urls import path
from . import views
from django.urls import path
from . import views


app_name = 'core'

urlpatterns = [
    path('', views.user_involved_map, name='user_involved_map'),
    path('signup_details/', views.signup_details, name='signup_details'),
    path('landingpage/', views.landingpage, name='landingpage'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('saved/', views.saved, name='saved'),
    path('email/', views.email, name='email'),
    path('admin_project_page/', views.admin_project_page, name='admin_project_page'),
    path('home/', views.home, name='home'),
    path('user_involved_map/', views.user_involved_map, name='user_involved_map'),
    path('organization/', views.organization, name='organization'),
    path('profilepage/', views.profilepage, name='profilepage'),
    path('drive/auth/', views.google_drive_auth, name='google_drive_auth'),
    path('drive/callback/', views.google_drive_callback, name='google_drive_callback'),
    path('drive/upload/', views.upload_file_to_drive, name='upload_file_to_drive'),
    path('delete_files_from_drive/', views.delete_files_from_drive, name='delete_files_from_drive'),
    path('create_folder_in_drive/', views.create_folder_in_drive, name='create_folder_in_drive'),
    path('folder/<str:folder_id>/', views.view_folder_contents, name='view_folder_contents'),
    path('move-files-to-trash/', views.move_files_to_trash, name='move_files_to_trash'),
    path('empty-trash/', views.empty_trash, name='empty_trash'),
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('edit_user_profile/', views.edit_user_profile, name='edit_user_profile'),

    # FOR EDITING PROJECTS
    path('core/project/<int:project_id>/edit/', views.aa, name='aa'),
    # FOR DELETING PROJECTS
    path('core/project/<int:project_id>/delete/', views.delete_project, name='delete_project'),


    # PRACTICE TEMPLATES
    path('practice/', views.practice, name='practice'),
    path('practice1/', views.practice1, name='practice1'),
]
