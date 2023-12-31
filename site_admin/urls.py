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
from django.contrib.auth import views as auth_views
from .views import staff_view, staff_detail, staff_save

app_name = 'site_admin'
urlpatterns = [
    path('staff/', staff_view, name='staff-view'),
    path('staff_context/<str:title>', staff_view, name='staff-view-context'),
    path('staff_detail/<str:username>', staff_detail, name='staff-detail'),
    path('staff_save/', staff_save, name='staff-save'),
]
