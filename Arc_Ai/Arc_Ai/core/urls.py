from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.organization, name='organization'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('saved/', views.saved, name='saved'),
    path('email/', views.email, name='email'),
    path('home/', views.home, name='home'),
]
