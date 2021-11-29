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
from .views import (config_generator,
                    create_generator,
                    detail_generator,
                    delete_generator,
                    save_generator,
                    ajax_generate,)

app_name = 'generators'
urlpatterns = [
    path('config/', config_generator, name='generator-config'),
    path('list/<str:success>/', config_generator, name='generator-config-success'),
    path('create/', create_generator, name='generator-create'),
    path('detail/<slug:use_area>/', detail_generator, name='generator-detail'),
    path('delete/<slug:use_area>/', delete_generator, name='generator-delete'),
    path('save/', save_generator, name='generator-save'),
    path('ajax_genarate/', ajax_generate, name='ajax-generate')
]
