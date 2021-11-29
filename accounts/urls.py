"""Tekhnoritm_Web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from .views import CustomLoginView, profile_view, signup
from django.contrib.auth import views as auth_views

app_name = 'accounts'
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('custom_login/', CustomLoginView.as_view(), name='custom-login'),
    path('profile/', profile_view, name='profile'),
    path('create/', signup, name='account-create'),
    #path('custom_logout/', auth_views.LogoutView.as_view(), {'next_page': '/accounts/login/'}),
    # path('create/', signup, name='account_create'),
    # path('profile/', profile, name='account_profile')
]
