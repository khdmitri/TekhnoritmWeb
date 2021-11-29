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

from django.urls import path
from .views import (init_workflow,
                    cleric_view,
                    inspection_view,
                    laboratory_view,
                    hide_message,
                    )

app_name = 'workflow'
urlpatterns = [
    path('', init_workflow, name='home'),
    path('cleric/', cleric_view, name='cleric-view'),
    path('inspection', inspection_view, name='inspection-view'),
    path('laboratory', laboratory_view, name='laboratory-view'),
    path('hide_message/<str:msg_type>/<int:msg_id>/', hide_message, name='hide-message'),
    # path('create/', signup, name='account_create'),
    # path('profile/', profile, name='account_profile')
]
