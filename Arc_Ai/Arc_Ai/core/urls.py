from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.email, name='email'),
    path('signup/', views.signup, name='signup'),
    path('organization/', views.organization, name='organization'),
    path('saved/', views.saved, name='saved'),
    path('email/', views.email, name='email'),
    # path('login/', views.login, name='login'),
    path('home/', views.home, name='home'),
]
