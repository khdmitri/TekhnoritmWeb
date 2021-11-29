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
from .views import show_messages, create_message, detail_message, answer_message, close_topic, detail_alert

app_name = 'int_messages'
urlpatterns = [
    path('create/', create_message, name='message-create'),
    path('detail/<int:message_id>/<slug:parent_box>/', detail_message, name='message-detail'),
    path('alert_detail/<int:alert_id>/', detail_alert, name='alert-detail'),
    path('answer/', answer_message, name='message-answer'),
    path('close_message/<slug:ticket_id>/<str:parent_box>/', close_topic, name='topic-close'),
    path('show/<str:box>/<slug:type>/<slug:message>/', show_messages, name='message-list'),
]
