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
    show_upload_page,
    upload_post,
    ajax_search_list,
    search_rpn
)

app_name = 'rpn_searcher'
urlpatterns = [
    path('upload/', show_upload_page, name='upload-page'),
    path('upload_post/', upload_post, name='upload-post'),
    path('ajax_search_list/', ajax_search_list, name='ajax-rpn-search'),
    path('search_rpn/', search_rpn, name='search-rpn'),
]
