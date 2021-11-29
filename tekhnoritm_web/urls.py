"""tekhnoritm_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include, re_path
from .views import start_app
from django.conf.urls.static import static
from django.conf import settings
from .views import ajax_alarms, ajax_mark_as_red
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', start_app, name='start-app'),
    path('favicon.ico', RedirectView.as_view(url='/static/custom/favicon.ico'), name='favicon'),
    path('order_control/', include('order_control.urls')),
    path('rpn_searcher/', include('rpn_searcher.urls')),
    path('archive/', include('archive.urls')),
    path('laboratory/', include('laboratory.urls')),
    path('inspection/', include('inspection.urls')),
    path('orders/', include('orders.urls')),
    path('references/', include('references.urls')),
    path('generators/', include('generators.urls')),
    path('int_messages/', include('int_messages.urls')),
    path('site_admin/', include('site_admin.urls')),
    path('accounts/', include('accounts.urls')),
    path('workflow/', include('workflow.urls')),
    path('export', include('export.urls')),
    path('alarms/', ajax_alarms, name='ajax-alarm'),
    path('marks/', ajax_mark_as_red, name='ajax-mark-as-red'),
    path('admin/', admin.site.urls),
    re_path(r'^celery-progress/', include('celery_progress.urls')),  # the endpoint is configurable
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

