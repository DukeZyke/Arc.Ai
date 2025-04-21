from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('organization/', views.organization, name='organization'),
    path('saved/', views.saved, name='saved'),
    path('email/', views.email, name='email'),
]