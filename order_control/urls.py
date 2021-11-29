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
from .views import (
    show_target_list,
    control_config,
    add_person_to_alert,
    delete_person,
    delete_card,
    control_list,
    control_division,
    control_kind,
    kind_objects,
    control_executor,
    control_card,
    ajax_search_card,
)

app_name = 'order_control'
urlpatterns = [
    path('', show_target_list, name='target-list'),
    path('kind_objects/<str:action_id>/', kind_objects, name='kind-objects'),
    path('target_list_alert/<str:alert_message>/', show_target_list, name='target-list-alert'),
    path('control_list/', control_list, name='control-list'),
    path('control_division/', control_division, name='control-division'),
    path('control_kind/', control_kind, name='control-kind'),
    path('control_card/', control_card, name='control-card'),
    path('control_executor/', control_executor, name='control-executor'),
    path('config/<str:task_id>/', control_config, name='control-config'),
    path('add_person/', add_person_to_alert, name='add-person-to-alert'),
    path('delete_person/', delete_person, name='delete-person'),
    path('delete_card/<str:card_id>/', delete_card, name='delete-card'),
    path('ajax_search_card/', ajax_search_card, name='ajax-card-search'),
]
