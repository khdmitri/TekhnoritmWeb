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
from .views import (
    source_table,
    object_list,
    object_list_table,
    load_common_form,
    object_post,
    delete_object,
    ajax_search_list,
    source_data,
    see,
    protocol,
    ez,
    delete_source,
    source_post,
    source_list_table,
    add_to_reference,
    ajax_owner_search,
    see_data,
    document_post,
    load_document_tab,
    load_point_tab,
    refresh_doc_main,
    add_income_doc,
    add_income_doc_ref,
    delete_income_doc,
    delete_income_doc_ref,
    see_main_post,
    point_post,
    delete_point,
    load_zone_tab,
    load_szz_zone_tab,
    zone_post,
    szz_zone_post,
    generate_zones,
    delete_zone,
    load_extra_tab,
    extra_post,
    load_doc_low_content,
    delete_doc_low,
    load_ref_low,
    add_doc_low,
    load_ref_sign,
    sign_post,
    load_sign,
    delete_sign,
    doc_generation,
    generate_doc,
    download_doc,
    gen_see_post,
    protocol_data,
    protocol_main_post,
    load_proto_document_tab,
    load_protocol_point_tab,
    delete_protocol_point,
    protocol_point_post,
    add_service_room,
    gen_protocol_post,
    ez_data,
    ez_main_post,
    refresh_ez_main,
    load_document_ez_tab,
    add_income_ez_doc,
    add_income_ez_doc_ref,
    delete_income_ez_doc,
    delete_income_ez_doc_ref,
    document_ez_post,
    load_extra_ez_tab,
    load_szz_zone_ez_tab,
    generate_ez_zones,
    extra_ez_post,
    szz_zone_ez_post,
    gen_ez_post,
    gen_oos_post, ajax_dadata_address,
)

app_name = 'inspection'
urlpatterns = [
    path('source_table/', source_table, name='source-table'),
    path('object_list/<str:order_id>/', object_list, name='object-list'),
    path('object_list_table/', object_list_table, name='object-list-table'),
    path('source_list_table/', source_list_table, name='source-list-table'),
    path('delete_object/<int:object_id>/<str:order_id>/', delete_object, name='delete-object'),
    path('delete_source/<int:source_id>/<str:object_id>/', delete_source, name='delete-source'),
    path('load_common_form/', load_common_form, name='load-common-form'),
    path('object_post/', object_post, name='object-post'),
    path('source_post/', source_post, name='source-post'),
    path('ajax_client_search/', ajax_search_list, name='ajax-client-search'),
    path('source_data/<int:ref_object>/', source_data, name='source-data'),
    path('see/<int:ref_object>/', see, name='see'),
    path('protocol/<int:ref_object>/', protocol, name='protocol'),
    path('ez/<int:ref_object>/', ez, name='ez'),
    path('add_to_reference/', add_to_reference, name='add-to-reference'),
    path('ajax_owner_search/', ajax_owner_search, name='ajax-owner-search'),
    path('see_data/<int:ref_object>/', see_data, name='see-data'),
    path('ez_data/<int:ref_object>/', ez_data, name='ez-data'),
    path('protocol_data/<int:ref_object>/', protocol_data, name='protocol-data'),
    path('document_post/', document_post, name='document-post'),
    path('document_ez_post/', document_ez_post, name='document-ez-post'),
    path('sign_post/', sign_post, name='sign-post'),
    path('point_post/', point_post, name='point-post'),
    path('protocol_point_post/', protocol_point_post, name='protocol-point-post'),
    path('load_document_tab/', load_document_tab, name='load-document-tab'),
    path('load_document_ez_tab/', load_document_ez_tab, name='load-document-ez-tab'),
    path('load_proto_document_tab/', load_proto_document_tab, name='load-proto-document-tab'),
    path('load_extra_tab/', load_extra_tab, name='load-extra-tab'),
    path('load_extra_ez_tab/', load_extra_ez_tab, name='load-extra-ez-tab'),
    path('load_point_tab/', load_point_tab, name='load-point-tab'),
    path('load_protocol_point_tab/', load_protocol_point_tab, name='load-protocol-point-tab'),
    path('load_zone_tab/', load_zone_tab, name='load-zone-tab'),
    path('load_szz_zone_tab/', load_szz_zone_tab, name='load-szz-zone-tab'),
    path('load_szz_zone_ez_tab/', load_szz_zone_ez_tab, name='load-szz-zone-ez-tab'),
    path('refresh_doc_main/<int:see_id>/', refresh_doc_main, name='refresh-doc-main'),
    path('refresh_ez_main/<int:ez_id>/', refresh_ez_main, name='refresh-ez-main'),
    path('add_income_doc/', add_income_doc, name='add-income-doc'),
    path('add_income_ez_doc/', add_income_ez_doc, name='add-income-ez-doc'),
    path('add_income_doc_ref/', add_income_doc_ref, name='add-income-doc-ref'),
    path('add_income_ez_doc_ref/', add_income_ez_doc_ref, name='add-income-ez-doc-ref'),
    path('delete_income_doc/', delete_income_doc, name='delete-income-doc'),
    path('delete_income_ez_doc/', delete_income_ez_doc, name='delete-income-ez-doc'),
    path('delete_point/', delete_point, name='delete-point'),
    path('delete_protocol_point/', delete_protocol_point, name='delete-protocol-point'),
    path('delete_zone/', delete_zone, name='delete-zone'),
    path('delete_income_doc_ref/', delete_income_doc_ref, name='delete-income-doc-ref'),
    path('delete_income_ez_doc_ref/', delete_income_ez_doc_ref, name='delete-income-ez-doc-ref'),
    path('see_main_post/', see_main_post, name='see-main-post'),
    path('ez_main_post/', ez_main_post, name='ez-main-post'),
    path('protocol_main_post/', protocol_main_post, name='protocol-main-post'),
    path('zone_post/', zone_post, name='zone-post'),
    path('szz_zone_post/', szz_zone_post, name='szz-zone-post'),
    path('szz_zone_ez_post/', szz_zone_ez_post, name='szz-zone-ez-post'),
    path('extra_post/', extra_post, name='extra-post'),
    path('extra_ez_post/', extra_ez_post, name='extra-ez-post'),
    path('generate_zones/', generate_zones, name='generate-zones'),
    path('generate_ez_zones/', generate_ez_zones, name='generate-ez-zones'),
    path('load_doc_low_content/', load_doc_low_content, name='load-doc-low-content'),
    path('delete_doc_low/', delete_doc_low, name='delete-doc-low'),
    path('delete_sign/', delete_sign, name='delete-sign'),
    path('load_ref_low/', load_ref_low, name='load-ref-low'),
    path('load_ref_sign/', load_ref_sign, name='load-ref-sign'),
    path('load_sign/', load_sign, name='load-sign'),
    path('add_doc_low/', add_doc_low, name='add-doc-low'),
    path('doc_generation/<int:ref_object>/', doc_generation, name='doc-generation'),
    path('generate_doc/<str:doc_type>/<int:ref_object>/', generate_doc, name='generate-doc'),
    path('download_doc/<str:doc_type>/<int:ref_object>/', download_doc, name='download-doc'),
    path('gen_see_post/', gen_see_post, name='gen-see-post'),
    path('gen_oos_post/', gen_oos_post, name='gen-oos-post'),
    path('gen_ez_post/', gen_ez_post, name='gen-ez-post'),
    path('gen_protocol_post/', gen_protocol_post, name='gen-protocol-post'),
    path('add_service_room/', add_service_room, name='add-service-room'),
    path('ajax_dadata_address/', ajax_dadata_address, name='dadata-address')
]
