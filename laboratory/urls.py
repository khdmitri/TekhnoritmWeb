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
from .views import (pribor_list,
                    ajax_pribor_list,
                    pribor_detail,
                    pribor_create,
                    pribor_delete,
                    pribor_save,
                    pribor_warn_list,
                    ref_protocol_emp,
                    add_pribor_ref,
                    delete_pribor,
                    source_table, )

app_name = 'laboratory'
urlpatterns = [
    path('source_table/', source_table, name='source-table'),
    path('pribor_list/', pribor_list, name='pribor-list'),
    path('pribor_warn_list/', pribor_warn_list, name='pribor-warn-list'),
    path('ajax_pribor_list/', ajax_pribor_list, name='ajax-pribor-search'),
    path('detail/<int:pribor_id>/', pribor_detail, name='pribor-detail'),
    path('pribor_list/<str:success>/', pribor_list, name='pribor-list-success'),
    path('pribor_create/', pribor_create, name='pribor-create'),
    path('pribor_delete/<int:pribor_id>/', pribor_delete, name='pribor-delete'),
    path('pribor_save/', pribor_save, name='pribor-save'),
    path('ref_protocol_emp/', ref_protocol_emp, name='ref-protocol-emp'),
    path('add_pribor_ref/', add_pribor_ref, name='add-pribor-ref'),
    path('delete_pribor/', delete_pribor, name='delete-pribor')
]
