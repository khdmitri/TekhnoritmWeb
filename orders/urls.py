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
    order_list,
    ajax_order_list,
    order_detail,
    order_create,
    order_save,
    ajax_search_list,
    order_task_create,
    order_task_detail,
    order_task_table_ajax,
    order_close,
    order_delete,
    order_task_close,
    order_task_delete,
    order_publicate_ajax,
    ajax_task_action_table,
    fill_default_actions,
    action_create,
    action_detail,
    action_delete,
    distribution_list,
    distribute,
    distribute_action,
    action_execute,
    in_process_list,
    execution_list,
    execution_detail,
    execution_post,
    action_close,
    delete_execution,
    control_order,
    close_order,
    close_task,
    delete_order,
    delete_task,
    expand_order,
    expand_task,
    ajax_control_order_search,
    ajax_control_task_search,
    ajax_control_action_search,
    ajax_control_card_search,
    delete_action,
    delete_card,
    expand_action,
    expand_card,
    card_create,
    card_detail,
    generate_request,
    preview_close_task,
    start_action,
    close_action,
    create_extended_order,
    ajax_client_contract,
    ajax_expand_contract,
    ajax_add_contract,
    ajax_remove_contract,
)

app_name = 'orders'
urlpatterns = [
    path('', order_list, name='order-list'),
    path('ajax_order_list/', ajax_order_list, name='ajax-order-search'),
    path('ajax_search_list/', ajax_search_list, name='ajax-client-search'),
    path('detail/<str:order_id>/', order_detail, name='order-detail'),
    path('task_detail/<str:task_id>/', order_task_detail, name='order-task-detail'),
    path('list/<str:success>/', order_list, name='order-list-success'),
    path('create/', order_create, name='order-create'),
    path('save/', order_save, name='order-save'),
    path('kind_create/<str:ref_order>/', order_task_create, name='order-kind-create'),
    path('detail_task_table/', order_task_table_ajax, name='ajax-order-task-table'),
    path('order_close/<str:order_id>/', order_close, name='order-close'),
    path('order_delete/<str:order_id>/', order_delete, name='order-delete'),
    path('order_task_close/<str:task_id>/', order_task_close, name='order-task-close'),
    path('order_task_delete/<str:task_id>/', order_task_delete, name='order-task-delete'),
    path('order_publicate/', order_publicate_ajax, name='ajax-order-publicate'),
    path('task_action_table/', ajax_task_action_table, name='ajax-task-action-table'),
    path('fill_default_actions/', fill_default_actions, name='fill-default-actions'),
    path('action_create/<str:task_id>/', action_create, name='action-create'),
    path('action_detail/<str:action_id>/', action_detail, name='action-detail'),
    path('action_delete/<int:task_id>/', action_delete, name='action-delete'),
    path('distribution_list/', distribution_list, name='distribution-list'),
    path('distribute/<str:task_id>/', distribute, name='distribute'),
    path('distribute_action/<str:task_id>/', distribute_action, name='distribute-action'),
    path('in_process/', in_process_list, name='in-process'),
    path('action_execute/<int:action_id>/', action_execute, name='action-execute'),
    path('execution_list/', execution_list, name='execution-list'),
    path('execution_detail/<str:execution_id>/', execution_detail, name='execution-detail'),
    path('execution_post/', execution_post, name='execution-post'),
    path('action_close/<int:action_id>/', action_close, name='action-close'),
    path('delete_execution/<int:execution_id>/<int:action_id>/', delete_execution, name='delete-execution'),
    path('control_order/', control_order, name='control-order'),
    path('close_order/<str:order_id>/', close_order, name='close-order'),
    path('delete_order/<str:order_id>/', delete_order, name='delete-order'),
    path('close_task/<str:task_id>/', close_task, name='close-task'),
    path('preview_close_task/<str:task_id>/', preview_close_task, name='preview-close-task'),
    path('delete_task/<str:task_id>/', delete_task, name='delete-task'),
    path('delete_action/<str:action_id>/', delete_action, name='delete-action'),
    path('close_action/', close_action, name='close-action'),
    path('delete_card/', delete_card, name='delete-card'),
    path('expand_order/', expand_order, name='expand-order'),
    path('expand_task/', expand_task, name='expand-task'),
    path('expand_action/', expand_action, name='expand-action'),
    path('start_action/', start_action, name='start-action'),
    path('expand_card/', expand_card, name='expand-card'),
    path('ajax_control_order_search/', ajax_control_order_search, name='ajax-control-order-search'),
    path('ajax_control_task_search/', ajax_control_task_search, name='ajax-control-task-search'),
    path('ajax_control_action_search/', ajax_control_action_search, name='ajax-control-action-search'),
    path('ajax_control_card_search/', ajax_control_card_search, name='ajax-control-card-search'),
    path('card_create/<int:ref_action>/', card_create, name='card-create'),
    path('card_detail/<int:execution_id>/', card_detail, name='card-detail'),
    path('generate_request/<int:action_id>/<str:doc_type>/', generate_request, name='generate-request'),
    path('create_extended_order/<str:master_id>/', create_extended_order, name='create-extended-order'),
    path('ajax_client_contract/', ajax_client_contract, name='ajax-client-contract'),
    path('ajax_expand_contract/', ajax_expand_contract, name='ajax-expand-contract'),
    path('ajax_add_contract/', ajax_add_contract, name='ajax-add-contract'),
    path('ajax_remove_contract/', ajax_remove_contract, name='ajax-remove-contract'),
]
