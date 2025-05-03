from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('saved/', views.saved, name='saved'),
    path('email/', views.email, name='email'),
    path('organization/', views.organization, name='organization'),
]
