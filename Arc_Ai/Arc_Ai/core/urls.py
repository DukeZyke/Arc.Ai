from django.urls import path
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('organization/', views.organization, name='organization'),
    path('saved/', views.saved, name='saved'),
    path('email/', views.email, name='email'),
]
