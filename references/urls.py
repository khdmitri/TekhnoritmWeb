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
from .views import (client_create,
                    client_list,
                    ajax_search_list,
                    client_detail,
                    client_save,
                    default_task_list,
                    default_task_create,
                    default_task_detail,
                    default_task,
                    default_task_delete,
                    show_ref_category,
                    load_category,
                    category_post,
                    delete_category_item,
                    client_delete,
                    load_request_person,
                    prepare_request_person,
                    request_person_post,
                    delete_request_person,
                    ajax_client_list,
                    get_available_contracts,
                    create_contract,
                    contract_detail,
                    client_contract,
                    expand_contract,
                    contract_delete,
                    contract_close,
                    )

app_name = 'references'
urlpatterns = [
    path('', client_list, name='client-list'),
    path('list/<str:success>/', client_list, name='client-list-success'),
    path('create/', client_create, name='client-create'),
    path('create_contract/', create_contract, name='create-contract'),
    path('create_contract/<int:client_id>/<int:contract_id>/', create_contract, name='create-contract-param'),
    path('ajax_search_list/', ajax_search_list, name='ajax-client-search'),
    path('ajax_client_list/', ajax_client_list, name='ajax-client-list'),
    path('get_available_contracts', get_available_contracts, name='get-available-contracts'),
    path('detail/<int:client_id>/', client_detail, name='client-detail'),
    path('save/', client_save, name='client-save'),
    path('default_task_detail/<int:task_id>/', default_task_detail, name='default-task-detail'),
    path('default_task_create/<str:task_type>/', default_task_create, name='default-task-create'),
    path('default_task_list/', default_task_list, name='default-task-list'),
    path('default_task/', default_task, name='default-task'),
    path('default_task_delete/<int:task_id>/', default_task_delete, name='default-task-delete'),
    path('show_ref_category/', show_ref_category, name='show-ref-category'),
    path('load_category/', load_category, name='load-category'),
    path('category_post/', category_post, name='category-post'),
    path('delete_category_item/', delete_category_item, name='delete-category-item'),
    path('client_delete/<int:client_id>', client_delete, name='client-delete'),
    path('load_request_person/<int:client_id>/', load_request_person, name='load-request-person'),
    path('prepare_request_person/', prepare_request_person, name='prepare-request-person'),
    path('request_person_post/', request_person_post, name='request-person-post'),
    path('delete_request_person/', delete_request_person, name='delete-request-person'),
    path('contract_detail/<int:contract_id>/', contract_detail, name='contract-detail'),
    path('client_contracts/<int:client_id>/', client_contract, name='client-contracts'),
    path('client_contracts/<int:client_id>/<str:alert_class>/<str:text>/', client_contract,
         name='client-contracts-message'),
    path('expand_contract/', expand_contract, name='expand-contract'),
    path('contract_delete/<int:contract_id>/', contract_delete, name='contract-delete'),
    path('contract_close/<int:contract_id>/', contract_close, name='contract-close'),
]
