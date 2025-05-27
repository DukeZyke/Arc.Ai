from django.urls import path
from . import views
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.landingpage, name='landingpage'),
    path('user_involved_map', views.user_involved_map, name='user_involved_map'),
    path('signup_details/', views.signup_details, name='signup_details'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('saved/', views.saved, name='saved'),
    path('email/', views.email, name='email'),
    path('admin_project_page/', views.admin_project_page, name='admin_project_page'),
    path('admin_edit_project_details/', views.admin_edit_project_details, name='admin_edit_project_details'),
    path('create_project/', views.create_project_details, name='create_project_details'),

    path('admin_users_page/', views.admin_users_page, name='admin_users_page'),
    path('home/', views.home, name='home'),
    path('user_involved_map/', views.user_involved_map, name='user_involved_map'),
    path('get_all_users_for_usermap/', views.get_all_users_for_usermap, name='get_all_users_for_usermap'),
    path('api/load-user-map/', views.load_user_map, name='load_user_map'),
    path('organization/', views.organization, name='organization'),
    path('get_project_details/<int:project_id>/', views.get_project_details, name='get_project_details'),
    path('profilepage/<int:pk>/', views.profilepage, name='profilepage'),
    path('edit_user_profile/<int:pk>/', views.edit_user_profile, name='edit_user_profile'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_signup/', views.admin_signup, name='admin_signup'),
    path('admin_files_page/', views.admin_files_page, name='admin_files_page'),

    # Addtional paths
    path('get_project_folder/<int:project_id>/', views.get_project_folder, name='get_project_folder'),
    path('get_project_details/<int:project_id>/', views.get_project_details, name='get_project_details'),
    path('drive/auth/', views.google_drive_auth, name='google_drive_auth'),
    path('drive/callback/', views.google_drive_callback, name='google_drive_callback'),
    path('drive/upload/', views.upload_file_to_drive, name='upload_file_to_drive'),
    path('delete_files_from_drive/', views.delete_files_from_drive, name='delete_files_from_drive'),
    path('create_folder_in_drive/', views.create_folder_in_drive, name='create_folder_in_drive'),
    path('folder/<str:folder_id>/', views.view_folder_contents, name='view_folder_contents'),
    path('move-files-to-trash/', views.move_files_to_trash, name='move_files_to_trash'),
    path('empty-trash/', views.empty_trash, name='empty_trash'),
    path('api/notifications/', views.get_notifications, name='get_notifications'),
    path('edit_user_profile/<int:pk>/', views.edit_user_profile, name='edit_user_profile'),
    path('restore-from-trash/', views.restore_from_trash, name='restore_from_trash'),
    path('delete_folders/', views.delete_folders, name='delete_folders'),
    path('delete_user/', views.delete_user, name='delete_user'),
    path('logout/', views.logout_view, name='logout'),   
    
    # FOR EDITING PROJECTS
    path('core/project/<int:project_id>/edit/', views.admin_edit_project_details, name='admin_edit_project_details'),
    # FOR DELETING PROJECTS
    path('core/project/<int:project_id>/delete/', views.delete_project, name='delete_project'),

]
