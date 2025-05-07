from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.signup_details, name='signup_details'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('saved/', views.saved, name='saved'),
    path('email/', views.email, name='email'),
    path('home/', views.home, name='home'),
    path('organization/', views.organization, name='organization'),
    path('profilepage/', views.profilepage, name='profilepage'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
]
