import json

from django.shortcuts import render, get_object_or_404
from orders.models import Task, Order
from references.models import Client, UniBook, UniBook2, PRTOType
from .forms import (IncomeDocumentForm, EvalPointsForm, ZoneForm, SZZZoneForm, ExtraForm, DocumentSignForm,
                    ResultDocumentForm,)
from .models import (InspectionObject, CommonObjectInfo, SourceData, SEE, IncomeDocument, EvalPoints, ZoneByPoints,
                     DocumentLow, DocumentSign, ResultDocument, Protocol, ProtocolPoints, EZ, IncomeDocumentEZ,)
from .forms import (CommonObjectInfoForm, InspectionObjectForm, SourceDataForm, SEEForm, ProtocolForm,
                    ProtocolPointsForm, EZForm, IncomeDocumentEZForm, ExtraEZForm, SZZZoneEZForm)
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.models import User
from inspection.service.see_generator import generate
from inspection.service.oos_generator import generate_oos
from inspection.service.protocol_generator import generate_protocol
from inspection.service.ez_generator import generate_ez
from inspection.service.file_processing import ms_word_to_pdf, sign_doc
from laboratory.models import ProtocolPribor
from django.core.files import File
from django.core.files.storage import default_storage
from .service_func import add_service_points, is_float, floatFloor
from .order_control import link_to_order
from itertools import groupby
from operator import attrgetter
import datetime


# Create your views here.

SOURCE_KIND = {
    '1': 'Проектируемое оборудование',
    '2': 'Существующее оборудование',
    '3': 'Сторонее оборудование'
}

STANDARD_FREQ = {
    '900': 'GSM-900',
    '800L': 'LTE-800',
    '1800': 'DCS-1800',
    '1800L': 'LTE-1800',
    '2100': 'IMT-2000/UMTS',
    '2600L': 'LTE-2600'
}


def source_table(request):
    tasks = Task.objects.filter(
        distribution_dep=request.user.profile.department).filter(
        close_date__isnull=True
    ).exclude(
        accept_date__isnull=True
    ).order_by('dead_line')

    orders = []
    for task in tasks:
        if task.ref_order not in orders:
            if not task.ref_order.close_date:
                orders.append(task.ref_order)

    return render(request, 'inspection/order_list.html', {'orders': orders})


def object_list(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    if order.master_id is not None:
        master_order = get_object_or_404(Order, order_id=order.master_id)
    else:
        master_order = None

    tasks = Task.objects.filter(ref_order=order)

    if master_order is not None:
        master_tasks = Task.objects.filter(ref_order=master_order)
        objects = InspectionObject.objects.filter(ref_order=master_order)
    else:
        master_tasks = None
        objects = InspectionObject.objects.filter(ref_order=order)

    context = {
        'order': order,
        'master_order': master_order,
        'tasks': tasks,
        'master_tasks': master_tasks,
        'objects': objects
    }

    return render(request, 'inspection/object_list.html', context)


def object_list_table(request):
    order_id = request.GET['order_id']
    order = get_object_or_404(Order, order_id=order_id)
    if order.master_id is not None:
        master_order = get_object_or_404(Order, order_id=order.master_id)
        objects = InspectionObject.objects.filter(ref_order=master_order)
    else:
        objects = InspectionObject.objects.filter(ref_order=order)

    return render(request, 'inspection/object_table.html', {'objects': objects})


def source_list_table(request):
    object_id = request.GET['object_id']
    object_ = get_object_or_404(InspectionObject, id=object_id)

    source_projects = SourceData.get_data_by_object_kind(object_, 1)
    source_exists = SourceData.get_data_by_object_kind(object_, 2)
    source_outs = SourceData.get_data_by_object_kind(object_, 3)

    context = {
        'source_projects': source_projects,
        'source_exists': source_exists,
        'source_outs': source_outs
    }

    return render(request, 'inspection/source_data_table.html', context)


def ajax_search_list(request):
    search_line = request.GET['search_line']
    what = request.GET['what']
    if what == 'owner':
        if search_line:
            clients = Client.objects.filter(
                is_owner=True).filter(
                Q(short_name__icontains=search_line) | Q(long_name__icontains=search_line))[:20]
        else:
            clients = Client.objects.filter(is_owner=True)[:20]
        context = {
            'clients': clients,
        }
        return render(request, 'inspection/client_list_ajax_owner.html', context)
    else:
        if search_line:
            clients = Client.objects.filter(
                is_project=True).filter(
                Q(short_name__icontains=search_line) | Q(long_name__icontains=search_line))[:20]
        else:
            clients = Client.objects.filter(is_project=True)[:20]
        context = {
            'clients': clients,
        }
        return render(request, 'inspection/client_list_ajax_project.html', context)


def load_common_form(request):
    context = {
        'project_formats': UniBook2.get_objects_by_category('project_formats')
    }
    if request.method == 'POST':
        order = get_object_or_404(Order, order_id=request.POST['ref_order'])
        if order.master_id is not None:
            master_order = get_object_or_404(Order, order_id=order.master_id)
            common = get_object_or_404(CommonObjectInfo, ref_order=master_order)
        else:
            common = get_object_or_404(CommonObjectInfo, ref_order=order)
        common_form = CommonObjectInfoForm(request.POST, instance=common)

        if common_form.is_valid():
            context = {
                'success': 'Общие данные были успешно отредактированы!',
                'project_formats': UniBook2.get_objects_by_category('project_formats')
            }
            common_form.save()
            if common_form.cleaned_data.get('ref_owner_id', None):
                owner = get_object_or_404(Client, id=common_form.cleaned_data['ref_owner_id'])
                common.ref_owner = owner
                common.save()
            if common_form.cleaned_data.get('ref_project_id', None):
                project = get_object_or_404(Client, id=common_form.cleaned_data['ref_project_id'])
                common.ref_project = project
                common.save()
            if common_form.cleaned_data.get('project_format', None):
                common.project_format = common_form.cleaned_data['project_format']
                common.save()

            context['order_id'] = order.order_id
            context['common'] = common
        context['common_form'] = common_form
    else:
        order = get_object_or_404(Order, order_id=request.GET['order_id'])
        if order.master_id is not None:
            master_order = get_object_or_404(Order, order_id=order.master_id)
            common = CommonObjectInfo.objects.get_or_create(ref_order=master_order)[0]
        else:
            common = CommonObjectInfo.objects.get_or_create(ref_order=order)[0]
        common_form = CommonObjectInfoForm(instance=common, initial={
            'ref_order': common.ref_order,
            'ref_owner': common.ref_owner,
            'ref_project': common.ref_project,
            'ref_owner_text': common.ref_owner.short_name if common.ref_owner else '',
            'ref_project_text': common.ref_project.short_name if common.ref_project else '',
            'ref_owner_id': common.ref_owner.id if common.ref_owner else '',
            'ref_project_id': common.ref_project.id if common.ref_project else '',
            'project_format': common.project_format
        })

        context = {
            'common_form': common_form,
            'order_id': order.order_id,
            'common': common,
            'project_formats': UniBook2.get_objects_by_category('project_formats')
        }

    return render(request, 'inspection/common_form.html', context)


def object_post(request):
    context = {}
    if request.method == 'POST':
        if request.POST.get('id', None):
            object_ = get_object_or_404(InspectionObject, id=request.POST['id'])
            form = InspectionObjectForm(request.POST, request.FILES, instance=object_)
        else:
            form = InspectionObjectForm(request.POST, request.FILES)
        if form.is_valid():
            if form.data.get('id', None):
                context = {
                    'success': 'Объект был успешно отредактирован!'
                }
            else:
                context = {
                    'success': 'Объект был успешно создан!'
                }
            object_ = form.save()
            object_.refresh_from_db()
            context['order_id'] = object_.ref_order.id
            context['object'] = object_
        context['form'] = form
        context['prto_types'] = PRTOType.get_types()
    else:
        ref_order = request.GET['ref_order']
        order = get_object_or_404(Order, order_id=ref_order)
        object_ = None
        if request.GET.get('id', None):
            object_ = get_object_or_404(InspectionObject, id=request.GET['id'])
            form =InspectionObjectForm(instance=object_)
        else:
            common_obj = CommonObjectInfo.objects.get_or_create(ref_order=order)[0]
            form = InspectionObjectForm(initial={'ref_order': order,
                                                 'build_purpose': common_obj.build_purpose})
        context = {
            'order_id': order.order_id,
            'form': form,
            'prto_types': PRTOType.get_types()
        }
        if object:
            context['object'] = object_
    return render(request, 'inspection/object_form.html', context)


def ajax_dadata_address(request):
    if request.is_ajax():
        body = request.GET.dict()
        print(body)
    return JsonResponse({'success': 'true'})


def source_post(request):
    context = {}
    if request.method == 'POST':
        if request.POST.get('id', None):
            source = get_object_or_404(SourceData, id=request.POST['id'])
            form = SourceDataForm(request.POST, instance=source)
        else:
            form = SourceDataForm(request.POST)
        if form.is_valid():
            if form.data.get('id', None):
                source = save_source(form.data['id'],
                            form,
                            form.cleaned_data['az_hor_sect_1'],
                            form.cleaned_data['az_vert_sect_1'])
                context = {
                    'success': 'Объект был успешно отредактирован!',
                    'source': source,
                    'no': source.no
                }
            else:
                source = save_source(None,
                                     form,
                                     form.cleaned_data['az_hor_sect_1'],
                                     form.cleaned_data['az_vert_sect_1'])
                if form.cleaned_data['az_hor_sect_2']:
                    save_source(None,
                                form,
                                form.cleaned_data['az_hor_sect_2'],
                                form.cleaned_data['az_vert_sect_2'])
                if form.cleaned_data['az_hor_sect_3']:
                    save_source(None,
                                form,
                                form.cleaned_data['az_hor_sect_3'],
                                form.cleaned_data['az_vert_sect_3'])
                context = {
                    'success': 'Объект был успешно создан!',
                    'source': source,
                    'no': source.no
                }
                object_ = source.ref_object
                object_.has_source = True
                # нужно формировать объект CARD

                object_.save()

        context['form'] = form
        context['kind_description'] = SOURCE_KIND[str(form.data['kind_code'])]
    else:
        ref_object = request.GET['ref_object']
        kind = 1
        if request.GET.get('kind', None):
            kind = request.GET['kind']
        object_ = get_object_or_404(InspectionObject, id=ref_object)
        source = None
        if request.GET.get('id', None):
            source = get_object_or_404(SourceData, id=request.GET['id'])
            form = SourceDataForm(instance=source)
            kind = source.kind_code
        else:
            form = SourceDataForm(initial={'ref_object': object_,
                                           'kind_code': kind,
                                           'kind_description': SOURCE_KIND[str(kind)]})
        context = {
            'form': form,
            'kind_description': SOURCE_KIND[str(kind)],
            'kind': kind
        }
        if source:
            context['source'] = source
            context['no'] = source.no

        references = {}
        references['row_types'] = UniBook.get_objects_by_category('row_types')
        references['antennas'] = UniBook.get_objects_by_category('antennas')
        references['modulations'] = UniBook.get_objects_by_category('modulations')
        context['references'] = references

    return render(request, 'inspection/source_data_form.html', context)


def save_source(source_id, form, az_hor, az_vert):
    if source_id:
        source = get_object_or_404(SourceData, id=source_id)
    else:
        object_ = form.cleaned_data['ref_object']
        common = get_object_or_404(CommonObjectInfo, ref_order=object_.ref_order)
        last_no = SourceData.get_last_no(form.cleaned_data['ref_object'], form.cleaned_data['kind_code'])
        if last_no['no__max'] is None:
            last_no['no__max'] = 0

        source = SourceData(ref_object=form.cleaned_data['ref_object'],
                            kind_code=form.cleaned_data['kind_code'],
                            kind_description=form.cleaned_data['kind_description'],
                            no=last_no['no__max']+1)
        if form.cleaned_data.get('owner_id', None):
            client = get_object_or_404(Client, id=form.cleaned_data['owner_id'])
            source.ref_owner = client
        else:
            source.ref_owner = common.ref_owner
        source.save()
    source.row_type = form.cleaned_data['row_type']
    source.power = form.cleaned_data['power']
    source.qty = form.cleaned_data['qty']
    source.freq = form.cleaned_data['freq']
    source.modulation = form.cleaned_data['modulation']
    source.antenna = form.cleaned_data['antenna']
    source.gain = form.cleaned_data['gain']
    source.high = form.cleaned_data['high']
    source.power_fact = form.cleaned_data['power_fact']
    source.dn = form.cleaned_data['dn']
    source.az_hor = az_hor
    source.az_vert = az_vert
    source.save()
    return source


def delete_object(request, object_id, order_id):
    object_ = get_object_or_404(InspectionObject, id=object_id)
    object_.delete()
    context = {
        'order_id': order_id
    }
    return HttpResponseRedirect(reverse('inspection:object-list', kwargs=context))


def source_data(request, ref_object):
    object_ = get_object_or_404(InspectionObject, id=ref_object)

    context = {
        'object': object_,
    }

    return render(request, 'inspection/source_data.html', context)


def see(request, ref_object):
    pass


def protocol(request, ref_object):
    pass


def ez(request, ref_object):
    pass


def delete_source(request, source_id, object_id):
    source = get_object_or_404(SourceData, id=source_id)
    source.delete()
    context = {
        'ref_object': object_id
    }
    return HttpResponseRedirect(reverse('inspection:source-data', kwargs=context))


def add_to_reference(request):
    category = request.GET['category']
    item = request.GET['item']
    if UniBook.add_new_record(category, item):
        data = {'success': True}
    else:
        data = {'success': False}

    return JsonResponse(data)


def ajax_owner_search(request):
    search_line = request.GET['search_line']
    if search_line:
        clients = Client.objects.filter(
            is_owner=True
        ).filter(
            Q(short_name__icontains=search_line) | Q(long_name__icontains=search_line))[:20]
    else:
        clients = Client.objects.filter(
            is_owner=True
        )[:20]
    context = {
        'clients': clients,
    }
    return render(request, 'inspection/owner_list_ajax.html', context)


def see_data(request, ref_object):
    object_ = get_object_or_404(InspectionObject, id=ref_object)
    see_model = SEE.objects.filter(ref_object=ref_object).last()
    if see_model:
        see_form = SEEForm(instance=see_model)
    else:
        common = get_object_or_404(CommonObjectInfo, ref_order=object_.ref_order)
        source_data = SourceData.get_data_by_object(object_)
        extra_staff = UniBook2.get_object_by_cat_short('see_extra', 'extra_staff')
        see_model = SEE.objects.create(ref_object=object_,
                                       project_header=project_format_constructor(common.project_format, object_, standard=standard_constructor(source_data)),
                                       standard=standard_constructor(source_data),
                                       freq=freq_constructor(source_data),
                                       az=az_constructor(source_data),
                                       extra_staff=extra_staff.item_long)

        see_form = SEEForm(instance=see_model)

        object_.has_see = True
        object_.save()

    context = {
        'form': see_form,
        'object_': object_,
        'see_model': see_model
    }

    return render(request, 'inspection/see_data.html', context)


def ez_data(request, ref_object):
    object_ = get_object_or_404(InspectionObject, id=ref_object)
    ez_model = EZ.objects.filter(ref_object=ref_object).last()
    see_model = SEE.objects.get(ref_object=object_)
    if ez_model:
        ez_form = EZForm(instance=ez_model)
    else:
        common = get_object_or_404(CommonObjectInfo, ref_order=object_.ref_order)
        source_data = SourceData.get_data_by_object(object_)
        ez_model = EZ.objects.create(ref_object=object_,
                                     standard=standard_constructor(source_data),
                                     freq=freq_constructor(source_data),
                                     az=az_constructor(source_data))
        if see_model:
            ez_model.szz = see_model.szz
            ez_model.low = see_model.low
            ez_model.extra = see_model.extra
            ez_model.extra_staff = see_model.extra_staff

        ez_form = EZForm(instance=ez_model)

        object_.has_ez = True
        object_.save()

    context = {
        'form': ez_form,
        'object_': object_,
        'ez_model': ez_model
    }

    return render(request, 'inspection/ez_data.html', context)


def protocol_data(request, ref_object):
    object_ = get_object_or_404(InspectionObject, id=ref_object)
    source_data = SourceData.get_data_by_object(object_)
    protocol_model = get_or_none(Protocol, ref_object=ref_object)
    if protocol_model:
        protocol_form = ProtocolForm(instance=protocol_model)
    else:
        pribors = ProtocolPribor.get_pribors_by_kind(0)
        protocol_model = Protocol.objects.create(ref_object=object_, standard=standard_constructor(source_data))
        for pribor in pribors:
            protocol_model.pribors.add(pribor)
        protocol_model.save()
        protocol_form = ProtocolForm(instance=protocol_model)

        object_.has_protocol = True
        object_.save()

    context = {
        'protocol_form': protocol_form,
        'object_': object_,
        'protocol_model': protocol_model
    }

    return render(request, 'inspection/protocol_data.html', context)


def see_main_post(request):
    if request.method == 'POST':
        see_model = get_object_or_404(SEE, see_id=request.POST['see_id'])
        see_form = SEEForm(request.POST, instance=see_model)
        object_ = see_model.ref_object

        success = None
        if see_form.is_valid():
            see_form.save()
            success = 'Успешно сохранено!'

        context = {
            'form': see_form,
            'object_': object_,
            'see_model': see_model
        }
        if success:
            context['success'] = success
    else:
        context = {}

    return render(request, 'inspection/see_data.html', context)


def ez_main_post(request):
    if request.method == 'POST':
        ez_model = get_object_or_404(EZ, ez_id=request.POST['ez_id'])
        ez_form = EZForm(request.POST, instance=ez_model)
        object_ = ez_model.ref_object

        success = None
        if ez_form.is_valid():
            ez_form.save()
            success = 'Успешно сохранено!'

        context = {
            'form': ez_form,
            'object_': object_,
            'ez_model': ez_model
        }
        if success:
            context['success'] = success
    else:
        context = {}

    return render(request, 'inspection/ez_data.html', context)


def protocol_main_post(request):
    if request.method == 'POST':
        protocol_model = get_object_or_404(Protocol, protocol_id=request.POST['protocol_id'])
        protocol_form = ProtocolForm(request.POST, instance=protocol_model)
        object_ = protocol_model.ref_object

        success = None
        if protocol_form.is_valid():
            protocol_form.save()
            success = 'Успешно сохранено!'

        context = {
            'protocol_form': protocol_form,
            'object_': object_,
            'protocol_model': protocol_model
        }
        if success:
            context['success'] = success
    else:
        context = {}

    return render(request, 'inspection/protocol_data.html', context)


def get_see_content(see_model, mode='edit'):
    if mode == 'edit':
        context = {
            'docs': IncomeDocument.get_docs_by_see(see_model),
            'doc_list': UniBook2.get_objects_by_category('income_docs'),
            'points': EvalPoints.get_points_by_see(see_model),
            'zones': ZoneByPoints.get_zone_by_see(see_model),
            'container': UniBook.get_objects_by_category('container'),
            'container_location': UniBook.get_objects_by_category('container_location'),
            'antenna_location': UniBook.get_objects_by_category('antenna_location'),
        }
    else:
        context = {
            'doc_list': UniBook.get_objects_by_category('income_docs'),
            'container': UniBook.get_objects_by_category('container'),
            'container_location': UniBook.get_objects_by_category('container_location'),
            'antenna_location': UniBook.get_objects_by_category('antenna_location'),
        }
    return context


def project_format_constructor(project_header, object_, standard=''):
    if project_header:
        if object_.address is None:
            object_.address = ''
        project = project_header.replace('#Address', object_.address)
        if object_.name is None:
            object_.name = ''
        project = project.replace('#BSName', object_.name)
        if standard is None:
            standard = ''
        project = project.replace('#Standard', standard)
        common = get_object_or_404(CommonObjectInfo, ref_order=object_.ref_order)
        if common.ref_owner.short_name is None:
            common.ref_owner.short_name = ''
        project = project.replace('#BSOwner', common.ref_owner.short_name)

        return project
    return None


def standard_constructor(source_data):
    freq_data_obj = source_data.filter(Q(kind_code=1) | Q(kind_code=2))
    freq_data = freq_data_obj.order_by('freq').values('freq').distinct()
    standard = None
    for freq in freq_data:
        if standard:
            if STANDARD_FREQ.get(freq['freq'], None):
                standard += '/'+STANDARD_FREQ[freq['freq']]
        else:
            if STANDARD_FREQ.get(freq['freq'], None):
                standard = STANDARD_FREQ[freq['freq']]

    return standard


def freq_constructor(source_data):
    freq_list = []
    freq_data_obj = source_data.filter(Q(kind_code=1) | Q(kind_code=2))
    freq_data = freq_data_obj.order_by('freq').values('freq').distinct()
    for freq in freq_data:
        freq_str = str(freq['freq']).replace('L', '')
        if freq_str not in freq_list:
            freq_list.append(freq_str+'МГц')

    freq_str = None
    for freq in freq_list:
        if freq_str:
            freq_str += '/'+freq
        else:
            freq_str = freq

    return freq_str


def az_constructor(source_data, kind='short'):
    type_1_obj = source_data.filter(kind_code=1)
    type_2_obj = source_data.filter(kind_code=2)
    type_3_obj = source_data.filter(kind_code=3)

    type_1 = type_1_obj.order_by('az_hor').values('az_hor').distinct()
    type_2 = type_2_obj.order_by('az_hor').values('az_hor').distinct()
    type_3 = type_3_obj.order_by('az_hor').values('az_hor').distinct()

    az_list = []
    if kind != 'short':
        for az in type_1:
            eval_az = az['az_hor']+'\u00b0'
            if eval_az not in az_list:
                az_list.append(eval_az)
        for az in type_2:
            eval_az = az['az_hor']+'\u00b0'
            if eval_az not in az_list:
                az_list.append(eval_az)
        for az in type_3:
            eval_az = az['az_hor']+'\u00b0'
            if eval_az not in az_list:
                az_list.append(eval_az)
    else:
        for az in type_1:
            eval_az = az['az_hor']+'\u00b0'
            if eval_az not in az_list:
                az_list.append(eval_az)
        for az in type_2:
            eval_az = az['az_hor']+'\u00b0'
            if eval_az not in az_list:
                az_list.append(eval_az)

    az_str = None
    for az in az_list:
        if az_str:
            az_str += '/'+az
        else:
            az_str = az

    return az_str


def load_document_tab(request):
    see_model = get_object_or_404(SEE, see_id=request.GET['see_id'])
    context = {
        'docs': IncomeDocument.get_docs_by_see(see_model),
        'doc_list': UniBook2.get_objects_by_category('income_docs')
    }

    if not context['docs']:
        item_protocol = UniBook2.get_object_by_cat_short('income_docs', 'Проект')
        presentation = item_protocol.item_long.replace('#project_name', see_model.project_header)
        IncomeDocument.objects.create(ref_see=see_model, short_name='Проект', presentation=presentation)

        item_protocol = UniBook2.get_object_by_cat_short('income_docs', 'План')
        presentation = item_protocol.item_long
        IncomeDocument.objects.create(ref_see=see_model, short_name='План', presentation=presentation)

        item_protocol = UniBook2.get_object_by_cat_short('income_docs', 'Расчет')
        presentation = item_protocol.item_long
        IncomeDocument.objects.create(ref_see=see_model, short_name='Расчет', presentation=presentation)

        item_protocol = UniBook2.get_object_by_cat_short('income_docs', 'Графика')
        presentation = item_protocol.item_long
        IncomeDocument.objects.create(ref_see=see_model, short_name='Графика', presentation=presentation)

    doc_form = IncomeDocumentForm(initial={
        'ref_see': see_model
    })

    context['doc_form'] = doc_form
    context['see_id'] = see_model.see_id

    return render(request, 'inspection/income_doc_form.html', context)


def load_document_ez_tab(request):
    ez_model = get_object_or_404(EZ, ez_id=request.GET['ez_id'])
    context = {
        'docs': IncomeDocumentEZ.get_docs_by_ez(ez_model),
        'doc_list': UniBook2.get_objects_by_category('income_ez_docs')
    }

    if not context['docs']:
        object_ = ez_model.ref_object
        proto = Protocol.objects.get(ref_object=object_)
        proto_no = proto.protocol_no
        proto_date = proto.protocol_date
        see = SEE.objects.get(ref_object=object_)
        see_no = see.see_no
        see_date = see.see_date
        item_protocol = UniBook2.get_object_by_cat_short('income_ez_docs', 'Протокол')
        presentation = item_protocol.item_long.replace('#proto_no', proto_no).replace(
                                                       '#proto_date', proto_date.strftime('%d.%m.%Y'))
        IncomeDocumentEZ.objects.create(ref_ez=ez_model, short_name='protocol', presentation=presentation)
        item_protocol = UniBook2.get_object_by_cat_short('income_ez_docs', 'СЭЭ')
        if see_no is None:
            see_no = '-'
        if see_date is None:
            see_date = datetime.date.today()
        presentation = item_protocol.item_long.replace('#see_no', see_no).replace(
                                                       '#see_date', see_date.strftime('%d.%m.%Y'))
        IncomeDocumentEZ.objects.create(ref_ez=ez_model, short_name='see', presentation=presentation)
        context['docs'] = IncomeDocumentEZ.get_docs_by_ez(ez_model)
        item_protocol = UniBook2.get_object_by_cat_short('income_ez_docs', 'План')
        IncomeDocumentEZ.objects.create(ref_ez=ez_model, short_name='План', presentation=item_protocol.item_long)

    doc_form = IncomeDocumentForm(initial={
        'ref_ez': ez_model
    })

    context['doc_form'] = doc_form
    context['ez_id'] = ez_model.ez_id

    return render(request, 'inspection/income_doc_ez_form.html', context)


def load_proto_document_tab(request):
    context = {
        'pribors': ProtocolPribor.get_data_by_kind(0),
        'my_evals': DocumentLow.get_items_by_types('protocol', 'evals'),
        'my_methods': DocumentLow.get_items_by_types('protocol', 'methods')
    }

    return render(request, 'inspection/proto_document.html', context)


def load_extra_tab(request):
    see_model = get_object_or_404(SEE, see_id=request.GET['see_id'])
    context = {
        'container_list': UniBook.get_objects_by_category('containers'),
        'location_list': UniBook.get_objects_by_category('locations'),
        'antenna_list': UniBook.get_objects_by_category('antenna_locations'),
    }

    extra_form = ExtraForm(instance=see_model)

    context['extra_form'] = extra_form
    context['see_id'] = see_model.see_id

    return render(request, 'inspection/extra_form.html', context)


def load_extra_ez_tab(request):
    ez_model = get_object_or_404(EZ, ez_id=request.GET['ez_id'])

    if not ez_model.extra:
        see_model = SEE.objects.get(ref_object=ez_model.ref_object)
        if see_model:
            ez_model.extra = see_model.extra
            ez_model.save()
    if not ez_model.extra_staff:
        see_model = SEE.objects.get(ref_object=ez_model.ref_object)
        if see_model:
            ez_model.extra_staff = see_model.extra_staff
            ez_model.save()

    extra_form = ExtraEZForm(instance=ez_model)
    context = {
        'extra_form': extra_form,
        'ez_id': ez_model.ez_id
    }

    return render(request, 'inspection/extra_ez_form.html', context)


def load_szz_zone_tab(request):
    see_model = get_object_or_404(SEE, see_id=request.GET['see_id'])
    context = {}

    szz_zone_form = SZZZoneForm(instance=see_model)

    context['szz_zone_form'] = szz_zone_form
    context['see_id'] = see_model.see_id

    return render(request, 'inspection/szz_zone_form.html', context)


def load_szz_zone_ez_tab(request):
    ez_model = get_object_or_404(EZ, ez_id=request.GET['ez_id'])
    context = {}

    if not ez_model.szz or not ez_model.low:
        see_model = SEE.objects.get(ref_object=ez_model.ref_object)
        if see_model:
            ez_model.szz = see_model.szz
            ez_model.low = see_model.low

    szz_zone_form = SZZZoneEZForm(instance=ez_model)

    context['szz_zone_form'] = szz_zone_form
    context['ez_id'] = ez_model.ez_id

    return render(request, 'inspection/szz_zone_ez_form.html', context)


def load_zone_tab(request):
    see_model = get_object_or_404(SEE, see_id=request.GET['see_id'])
    sd = SourceData.get_data_by_object(see_model.ref_object)
    zones = ZoneByPoints.get_zone_by_see(see_model)
    if not zones:
        points = calc_zone_points(sd, kind='long')
        for point in points:
            ZoneByPoints.objects.create(ref_see=see_model,
                                        az=point['az'],
                                        high=point['high'],
                                        distance=point['distance'],
                                        point_type=point['point_type'])

    context = {
        'zones': ZoneByPoints.get_zone_by_see(see_model),
    }

    zone_form = ZoneForm(initial={
        'ref_see': see_model
    })

    context['zone_form'] = zone_form
    context['see_id'] = see_model.see_id

    return render(request, 'inspection/zone_form.html', context)


def load_point_tab(request):
    see_model = get_object_or_404(SEE, see_id=request.GET['see_id'])
    context = {
        'points': EvalPoints.get_points_by_see(see_model),
    }

    last_no_plan = EvalPoints.get_last_no_plan(see_model)
    if last_no_plan['no_plan__max'] is None:
        last_no_plan['no_plan__max'] = 0
    point_form = EvalPointsForm(initial={
        'ref_see': see_model,
        'no_plan': last_no_plan['no_plan__max'] + 1
    })

    context['point_form'] = point_form
    context['see_id'] = see_model.see_id
    context['cur_no_plan'] = last_no_plan['no_plan__max']+1

    return render(request, 'inspection/point_form.html', context)


def load_protocol_point_tab(request):
    protocol_model = get_object_or_404(Protocol, protocol_id=request.GET['protocol_id'])
    context = {
        'points': ProtocolPoints.get_points_by_protocol(protocol_model),
    }

    cur_no_plan = ProtocolPoints.get_last_no_plan(protocol_model)['no_plan__max'] + 1
    protocol_point_form = ProtocolPointsForm(initial={
        'ref_protocol': protocol_model,
        'no': ProtocolPoints.get_last_no(protocol_model)['no__max'] + 1,
        'no_plan': cur_no_plan,
    })

    context['point_form'] = protocol_point_form
    context['protocol_id'] = protocol_model.protocol_id
    context['cur_no_plan'] = cur_no_plan

    return render(request, 'inspection/protocol_point_form.html', context)


def document_post(request):
    context = {}
    if request.method == 'POST':
        form = IncomeDocumentForm(request.POST)
        see_model = get_object_or_404(SEE, see_id=form.data['ref_see'])
        if form.is_valid():
            post = form.save()
            post.refresh_from_db()
            context = {
                'docs': IncomeDocument.get_docs_by_see(see_model),
                'doc_list': UniBook2.get_objects_by_category('income_docs')
            }
        doc_form = IncomeDocumentForm(initial={
            'ref_see': see_model
        })
        context['doc_form'] = doc_form
        context['see_id'] = see_model.see_id

    return render(request, 'inspection/income_doc_form.html', context)


def document_ez_post(request):
    context = {}
    if request.method == 'POST':
        form = IncomeDocumentEZForm(request.POST)
        ez_model = get_object_or_404(EZ, ez_id=form.data['ref_ez'])
        if form.is_valid():
            post = form.save()
            post.refresh_from_db()
            context = {
                'docs': IncomeDocumentEZ.get_docs_by_ez(ez_model),
                'doc_list': UniBook2.get_objects_by_category('income_ez_docs')
            }
        doc_form = IncomeDocumentEZForm(initial={
            'ref_ez': ez_model
        })
        context['doc_form'] = doc_form
        context['ez_id'] = ez_model.ez_id

    return render(request, 'inspection/income_doc_ez_form.html', context)


def sign_post(request):
    context = {}
    if request.method == 'POST':
        form = DocumentSignForm(request.POST)
        if form.is_valid():
            doc_type = form.cleaned_data['document_type']
            post = form.save()
            post.refresh_from_db()
            context = {
                'signs': DocumentSign.get_sign_by_type(doc_type),
            }
            form = DocumentSignForm(initial={
                'document_type': doc_type
            })
        context['sign_form'] = form

    return render(request, 'inspection/sign_content.html', context)


def point_post(request):
    context = {}
    if request.method == 'POST':
        form = EvalPointsForm(request.POST)
        see_model = get_object_or_404(SEE, see_id=form.data['ref_see'])
        if form.is_valid():
            post = form.save()
            post.refresh_from_db()
            eval_point = get_object_or_404(EvalPoints, id=post.pk)
            last_no = EvalPoints.get_last_no(eval_point.ref_see)
            if last_no['no__max'] is None:
                last_no['no__max'] = 0
            eval_point.no = last_no['no__max']+1
            eval_point.save()
            context = {
                'points': EvalPoints.get_points_by_see(see_model),
            }

        last_no_plan = EvalPoints.get_last_no_plan(see_model)
        if last_no_plan['no_plan__max'] is None:
            last_no_plan['no_plan__max'] = 0
        point_form = EvalPointsForm(initial={
            'ref_see': see_model,
            'no_plan': last_no_plan['no_plan__max']+1
        })
        context['point_form'] = point_form
        context['see_id'] = see_model.see_id
        context['cur_no_plan'] = last_no_plan['no_plan__max'] + 1

    return render(request, 'inspection/point_form.html', context)


def protocol_point_post(request):
    context = {}
    if request.method == 'POST':
        form = ProtocolPointsForm(request.POST)
        protocol_model = get_object_or_404(Protocol, protocol_id=form.data['ref_protocol'])
        last_no_plan = ProtocolPoints.get_last_no_plan(protocol_model)
        if last_no_plan['no_plan__max'] is None:
            last_no_plan['no_plan__max'] = 0
        if form.is_valid():
            post = form.save()
            post.refresh_from_db()
            protocol_point = get_object_or_404(ProtocolPoints, id=post.pk)
            last_no = ProtocolPoints.get_last_no(protocol_point.ref_protocol)
            if last_no['no__max'] is None:
                last_no['no__max'] = 0
            protocol_point.no = last_no['no__max']+1
            protocol_point.save()

            last_no_plan = ProtocolPoints.get_last_no_plan(protocol_model)
            if last_no_plan['no_plan__max'] is None:
                last_no_plan['no_plan__max'] = 0
            point_form = ProtocolPointsForm(initial={
                'ref_protocol': protocol_model,
                'no_plan': last_no_plan['no_plan__max']+1
            })
            context['point_form'] = point_form
        else:
            context['point_form'] = form
        context['points'] = ProtocolPoints.get_points_by_protocol(protocol_model)
        context['protocol_id'] = protocol_model.protocol_id
        context['cur_no_plan'] = last_no_plan['no_plan__max'] + 1

    return render(request, 'inspection/protocol_point_form.html', context)


def zone_post(request):
    context = {}
    if request.method == 'POST':
        if request.POST['id']:
            zone = get_object_or_404(ZoneByPoints, id=request.POST['id'])
            form = ZoneForm(request.POST, instance=zone)
            see_model = get_object_or_404(SEE, see_id=form.data['ref_see'])
            if form.is_valid():
                post = form.save()
                post.refresh_from_db()

            context = {
                'zones': ZoneByPoints.get_zone_by_see(see_model)
            }
        else:
            form = ZoneForm(request.POST)
            see_model = get_object_or_404(SEE, see_id=request.POST['ref_see'])

        context['zone_form'] = form
        context['see_id'] = see_model.see_id

    return render(request, 'inspection/zone_form.html', context)


def szz_zone_post(request):
    context = {}
    if request.method == 'POST':
        if request.POST['see_id']:
            see_model = get_object_or_404(SEE, see_id=request.POST['see_id'])
            form = SZZZoneForm(request.POST, instance=see_model)
            if form.is_valid():
                post = form.save()
                post.refresh_from_db()
                context['success'] = 'Успешно сохранено!'

            form = SZZZoneForm(instance=see_model)
            context['szz_zone_form'] = form
            context['see_id'] = see_model.see_id

    return render(request, 'inspection/szz_zone_form.html', context)


def szz_zone_ez_post(request):
    context = {}
    if request.method == 'POST':
        if request.POST['ez_id']:
            ez_model = get_object_or_404(EZ, ez_id=request.POST['ez_id'])
            form = SZZZoneEZForm(request.POST, instance=ez_model)
            if form.is_valid():
                post = form.save()
                post.refresh_from_db()
                context['success'] = 'Успешно сохранено!'

            form = SZZZoneEZForm(instance=ez_model)
            context['szz_zone_form'] = form
            context['ez_id'] = ez_model.ez_id

    return render(request, 'inspection/szz_zone_ez_form.html', context)


def extra_post(request):
    context = {
        'container_list': UniBook.get_objects_by_category('containers'),
        'location_list': UniBook.get_objects_by_category('locations'),
        'antenna_list': UniBook.get_objects_by_category('antenna_locations'),
    }
    if request.method == 'POST':
        if request.POST['see_id']:
            see_model = get_object_or_404(SEE, see_id=request.POST['see_id'])
            form = ExtraForm(request.POST, instance=see_model)
            if form.is_valid():
                post = form.save()
                post.refresh_from_db()
                context['success'] = 'Успешно сохранено!'

            form = ExtraForm(instance=see_model)
            context['extra_form'] = form
            context['see_id'] = see_model.see_id

    return render(request, 'inspection/extra_form.html', context)


def extra_ez_post(request):
    context = {
    }
    if request.method == 'POST':
        if request.POST['ez_id']:
            ez_model = get_object_or_404(EZ, ez_id=request.POST['ez_id'])
            form = ExtraEZForm(request.POST, instance=ez_model)
            if form.is_valid():
                post = form.save()
                post.refresh_from_db()
                context['success'] = 'Успешно сохранено!'

            form = ExtraEZForm(instance=ez_model)
            context['extra_form'] = form
            context['ez_id'] = ez_model.ez_id

    return render(request, 'inspection/extra_ez_form.html', context)


def add_income_doc(request):
    see_model = get_object_or_404(SEE, see_id=request.GET['see_id'])
    doc_id = request.GET['doc_id']

    # add new income document
    ref_doc = get_object_or_404(UniBook2, id=doc_id)
    presentation = ref_doc.item_long.replace('#project_name', see_model.project_header)

    doc = IncomeDocument.objects.create(ref_see=see_model, short_name=ref_doc.item_short, presentation=presentation)

    context = {
        'docs': IncomeDocument.get_docs_by_see(see_model),
        'doc_list': UniBook2.get_objects_by_category('income_docs')
    }

    if not context['docs']:
        item_protocol = UniBook2.get_object_by_cat_short('income_docs', 'Проект')
        presentation = item_protocol.item_long.replace('#project_name', see_model.project_header)
        IncomeDocument.objects.create(ref_see=see_model, short_name='Проект', presentation=presentation)

        item_protocol = UniBook2.get_object_by_cat_short('income_docs', 'План')
        presentation = item_protocol.item_long
        IncomeDocument.objects.create(ref_see=see_model, short_name='План', presentation=presentation)

        item_protocol = UniBook2.get_object_by_cat_short('income_docs', 'Расчет')
        presentation = item_protocol.item_long
        IncomeDocument.objects.create(ref_see=see_model, short_name='Расчет', presentation=presentation)

        item_protocol = UniBook2.get_object_by_cat_short('income_docs', 'Графика')
        presentation = item_protocol.item_long
        IncomeDocument.objects.create(ref_see=see_model, short_name='Графика', presentation=presentation)

    doc_form = IncomeDocumentForm(initial={
        'ref_see': see_model
    })

    context['doc_form'] = doc_form
    context['see_id'] = see_model.see_id

    return render(request, 'inspection/income_doc_form.html', context)


def add_income_ez_doc(request):
    ez_model = get_object_or_404(EZ, ez_id=request.GET['ez_id'])
    doc_id = request.GET['doc_id']

    # add new income document
    ref_doc = get_object_or_404(UniBook2, id=doc_id)
    object_ = ez_model.ref_object

    proto = Protocol.objects.get(ref_object=object_)
    proto_no = proto.protocol_no
    proto_date = proto.protocol_date
    see = SEE.objects.get(ref_object=object_)
    see_no = see.see_no
    see_date = see.see_date

    presentation = ref_doc.item_long.replace(
        '#proto_no', proto_no
    ).replace(
        '#proto_date', proto_date.strftime('%d.%m.%Y')
    ).replace(
        '#see_no', see_no
    ).replace(
        '#see_date', see_date.strftime('%d.%m.%Y')
    )

    doc = IncomeDocumentEZ.objects.create(ref_ez=ez_model, short_name=ref_doc.item_short, presentation=presentation)

    context = {
        'docs': IncomeDocumentEZ.get_docs_by_ez(ez_model),
        'doc_list': UniBook2.get_objects_by_category('income_ez_docs')
    }

    doc_form = IncomeDocumentEZForm(initial={
        'ref_ez': ez_model
    })

    context['doc_form'] = doc_form
    context['ez_id'] = ez_model.ez_id

    return render(request, 'inspection/income_doc_ez_form.html', context)


def add_income_doc_ref(request):
    see_model = get_object_or_404(SEE, see_id=request.GET['see_id'])
    item_short = request.GET['item_short']
    item_long = request.GET['item_long']

    # create new reference income document
    ref_doc = UniBook2.objects.create(category='income_docs', item_short=item_short, item_long=item_long)

    context = {
        'docs': IncomeDocument.get_docs_by_see(see_model),
        'doc_list': UniBook2.get_objects_by_category('income_docs')
    }

    doc_form = IncomeDocumentForm(initial={
        'ref_see': see_model
    })
    context['doc_form'] = doc_form
    context['see_id'] = see_model.see_id

    return render(request, 'inspection/income_doc_form.html', context)


def add_income_ez_doc_ref(request):
    ez_model = get_object_or_404(EZ, ez_id=request.GET['ez_id'])
    item_short = request.GET['item_short']
    item_long = request.GET['item_long']

    # create new reference income document
    ref_doc = UniBook2.objects.create(category='income_ez_docs', item_short=item_short, item_long=item_long)

    context = {
        'docs': IncomeDocumentEZ.get_docs_by_ez(ez_model),
        'doc_list': UniBook2.get_objects_by_category('income_ez_docs')
    }

    doc_form = IncomeDocumentEZForm(initial={
        'ref_ez': ez_model
    })
    context['doc_form'] = doc_form
    context['ez_id'] = ez_model.ez_id

    return render(request, 'inspection/income_doc_ez_form.html', context)


def delete_income_doc_ref(request):
    see_model = get_object_or_404(SEE, see_id=request.GET['see_id'])
    item_short = request.GET['item_short']
    item_long = request.GET['item_long']

    # create new reference income document
    ref_doc = UniBook2.objects.filter(item_short=item_short).filter(item_long=item_long)
    if ref_doc:
        ref_doc[0].delete()

    context = {
        'docs': IncomeDocument.get_docs_by_see(see_model),
        'doc_list': UniBook2.get_objects_by_category('income_docs')
    }

    doc_form = IncomeDocumentForm(initial={
        'ref_see': see_model
    })
    context['doc_form'] = doc_form
    context['see_id'] = see_model.see_id

    return render(request, 'inspection/income_doc_form.html', context)


def delete_income_ez_doc_ref(request):
    ez_model = get_object_or_404(EZ, ez_id=request.GET['ez_id'])
    item_short = request.GET['item_short']
    item_long = request.GET['item_long']

    ref_doc = UniBook2.objects.filter(item_short=item_short).filter(item_long=item_long)
    if ref_doc:
        ref_doc[0].delete()

    context = {
        'docs': IncomeDocumentEZ.get_docs_by_ez(ez_model),
        'doc_list': UniBook2.get_objects_by_category('income_ez_docs')
    }

    doc_form = IncomeDocumentEZForm(initial={
        'ref_ez': ez_model
    })
    context['doc_form'] = doc_form
    context['ez_id'] = ez_model.ez_id

    return render(request, 'inspection/income_doc_ez_form.html', context)


def delete_income_doc(request):
    see_model = get_object_or_404(SEE, see_id=request.GET['see_id'])
    doc_id = request.GET['doc_id']

    # delete income document
    doc = get_object_or_404(IncomeDocument, id=doc_id)
    doc.delete()

    context = {
        'docs': IncomeDocument.get_docs_by_see(see_model),
        'doc_list': UniBook2.get_objects_by_category('income_docs')
    }

    doc_form = IncomeDocumentForm(initial={
        'ref_see': see_model
    })
    context['doc_form'] = doc_form
    context['see_id'] = see_model.see_id

    return render(request, 'inspection/income_doc_form.html', context)


def delete_income_ez_doc(request):
    ez_model = get_object_or_404(EZ, ez_id=request.GET['ez_id'])
    doc_id = request.GET['doc_id']

    # delete income document
    doc = get_object_or_404(IncomeDocumentEZ, id=doc_id)
    doc.delete()

    context = {
        'docs': IncomeDocumentEZ.get_docs_by_ez(ez_model),
        'doc_list': UniBook2.get_objects_by_category('income_ez_docs')
    }

    doc_form = IncomeDocumentEZForm(initial={
        'ref_ez': ez_model
    })
    context['doc_form'] = doc_form
    context['ez_id'] = ez_model.ez_id

    return render(request, 'inspection/income_doc_ez_form.html', context)


def delete_point(request):
    see_model = get_object_or_404(SEE, see_id=request.GET['see_id'])
    point_id = request.GET['point_id']

    # delete control point
    point = get_object_or_404(EvalPoints, id=point_id)
    point.delete()

    points = EvalPoints.get_points_by_see(see_model)
    last_no = 0
    for point in points:
        last_no += 1
        point.no = last_no
        point.save()

    context = {
        'points': points,
    }

    point_form = EvalPointsForm(initial={
        'ref_see': see_model
    })
    context['point_form'] = point_form
    context['see_id'] = see_model.see_id

    return render(request, 'inspection/point_form.html', context)


def delete_protocol_point(request):
    protocol_model = get_object_or_404(Protocol, protocol_id=request.GET['protocol_id'])
    point_id = request.GET['point_id']

    # delete control point
    point = get_object_or_404(ProtocolPoints, id=point_id)
    point.delete()

    points = ProtocolPoints.get_points_by_protocol(protocol_model)
    last_no = 0
    for point in points:
        last_no += 1
        point.no = last_no
        point.save()

    context = {
        'points': points,
    }

    point_form = ProtocolPointsForm(initial={
        'ref_protocol': protocol_model
    })
    context['point_form'] = point_form
    context['protocol_id'] = protocol_model.protocol_id

    return render(request, 'inspection/protocol_point_form.html', context)


def add_service_room(request):
    protocol_model = get_object_or_404(Protocol, protocol_id=request.GET['protocol_id'])

    add_service_points(protocol_model)

    points = ProtocolPoints.get_points_by_protocol(protocol_model)
    last_no = 0
    for point in points:
        last_no += 1
        point.no = last_no
        point.save()

    context = {
        'points': points,
    }

    point_form = ProtocolPointsForm(initial={
        'ref_protocol': protocol_model
    })
    context['point_form'] = point_form
    context['protocol_id'] = protocol_model.protocol_id

    return render(request, 'inspection/protocol_point_form.html', context)


def delete_zone(request):
    see_model = get_object_or_404(SEE, see_id=request.GET['see_id'])
    zone_id = request.GET['zone_id']

    # delete control point
    zone = get_object_or_404(ZoneByPoints, id=zone_id)
    zone.delete()

    zones = ZoneByPoints.get_zone_by_see(see_model)

    context = {
        'zones': zones,
    }

    zone_form = ZoneForm(initial={
        'ref_see': see_model
    })
    context['zone_form'] = zone_form
    context['see_id'] = see_model.see_id

    return render(request, 'inspection/zone_form.html', context)


def get_or_none(model, *args, **kwargs):
    try:
        res_model = model.objects.get(*args, **kwargs)
        return res_model
    except model.DoesNotExist:
        return None


def refresh_doc_main(request, see_id):
    see_model = get_object_or_404(SEE, see_id=see_id)
    common = get_object_or_404(CommonObjectInfo, ref_order=see_model.ref_object.ref_order)
    source_data = SourceData.get_data_by_object(see_model.ref_object)
    see_model.project_header = project_format_constructor(common.project_format, see_model.ref_object, see_model.standard)
    see_model.standard = standard_constructor(source_data)
    see_model.freq = freq_constructor(source_data)
    see_model.az = az_constructor(source_data)
    see_model.save()

    see_form = SEEForm(instance=see_model)

    context = {
        'form': see_form,
        'object_': see_model.ref_object,
        'see_model': see_model
    }

    return render(request, 'inspection/see_data.html', context)


def refresh_ez_main(request, ez_id):
    ez_model = get_object_or_404(EZ, ez_id=ez_id)
    common = get_object_or_404(CommonObjectInfo, ref_order=ez_model.ref_object.ref_order)
    source_data = SourceData.get_data_by_object(ez_model.ref_object)
    ez_model.standard = standard_constructor(source_data)
    ez_model.project_header = project_format_constructor(common.project_format, ez_model.ref_object, standard=ez_model.standard)
    ez_model.freq = freq_constructor(source_data)
    ez_model.az = az_constructor(source_data)
    ez_model.save()

    ez_form = EZForm(instance=ez_model)

    context = {
        'form': ez_form,
        'object_': ez_model.ref_object,
        'ez_model': ez_model
    }

    return render(request, 'inspection/ez_data.html', context)


def calc_zone_points(source_data, kind='short'):
    type_1_obj = source_data.filter(kind_code=1)
    type_2_obj = source_data.filter(kind_code=2)
    type_3_obj = source_data.filter(kind_code=3)

    type_1_h = type_1_obj.order_by('high').values('high').distinct()
    h = 2.
    h_str = '2'
    for high in type_1_h:
        if is_float(high['high']):
            h_check = float(high['high'])
            if h_check > h:
                h = h_check
                h_str = high['high']
    type_1_h = h
    type_1_az_vert = type_1_obj.filter(high=h_str).order_by('az_vert').values('az_vert')
    az_vert_max = 0
    for az_vert in type_1_az_vert:
        if is_float(az_vert['az_vert']):
            az_vert_float = float(az_vert['az_vert'])
            if abs(az_vert_float) > az_vert_max:
                az_vert_max = abs(az_vert_float)
    type_1_h_max = type_1_h - az_vert_max

    type_1_az = type_1_obj.order_by('az_hor').values('az_hor').distinct()

    type_1 = []
    az_list = []
    for next_az in type_1_az:
        if next_az['az_hor'] not in az_list:
            az_list.append(next_az['az_hor'])
            type_1.append({'az': next_az['az_hor'],
                           'high': type_1_h_max,
                           'distance': '100',
                           'point_type': 1})

    type_2_h = type_2_obj.order_by('high').values('high').distinct()
    h = 2.
    h_str = '2'
    for high in type_2_h:
        if is_float(high['high']):
            h_check = float(high['high'])
            if h_check > h:
                h = h_check
                h_str = high['high']
    type_2_h = h
    type_2_az_vert = type_2_obj.filter(high=h_str).order_by('az_vert').values('az_vert')
    az_vert_max = 0
    for az_vert in type_2_az_vert:
        if is_float(az_vert['az_vert']):
            az_vert_float = float(az_vert['az_vert'])
            if abs(az_vert_float) > az_vert_max:
                az_vert_max = abs(az_vert_float)
    type_2_h_max = type_2_h - az_vert_max

    type_2_az = type_2_obj.order_by('az_hor').values('az_hor').distinct()

    type_2 = []
    for next_az in type_2_az:
        if next_az['az_hor'] not in az_list:
            az_list.append(next_az['az_hor'])
            type_2.append({'az': next_az['az_hor'],
                           'high': type_2_h_max,
                           'distance': '100',
                           'point_type': 2})

    if kind != 'short':
        type_3_h = type_3_obj.order_by('high').values('high').distinct()
        h = 2.
        h_str = '2'
        for high in type_3_h:
            if is_float(high['high']):
                h_check = float(high['high'])
                if h_check > h:
                    h = h_check
                    h_str = high['high']
        type_3_h = h
        type_3_az_vert = type_3_obj.filter(high=h_str).order_by('az_vert').values('az_vert')
        az_vert_max = 0
        for az_vert in type_3_az_vert:
            if is_float(az_vert['az_vert']):
                az_vert_float = float(az_vert['az_vert'])
                if abs(az_vert_float) > az_vert_max:
                    az_vert_max = abs(az_vert_float)
        type_3_h_max = type_3_h - az_vert_max

        type_3_az = type_3_obj.order_by('az_hor').values('az_hor').distinct()

        type_3 = []
        for next_az in type_3_az:
            if next_az['az_hor'] not in az_list:
                az_list.append(next_az['az_hor'])
                type_3.append({'az': next_az['az_hor'],
                               'high': type_3_h_max,
                               'distance': '100',
                               'point_type': 3})

        return type_1+type_2+type_3
    return type_1+type_2


def generate_zones(request):
    szz = request.GET['szz']
    unit = request.GET['unit']
    detailed = request.GET['detailed']
    see_model = get_object_or_404(SEE, see_id=request.GET['see_id'])

    templates = UniBook2.get_objects_by_category('zones')
    szz_description = templates.filter(item_short='szz_start').first().item_long
    szz_description += '\n'+templates.filter(item_short='szz').first().item_long
    szz_description = szz_description.replace('#SZZValue', szz+unit)

    zoz_points = ZoneByPoints.get_zone_by_see(see_model)
    eval_points = EvalPoints.get_points_by_see(see_model)
    zoz_description = templates.filter(item_short='zoz_start').first().item_long

    # Рассмотрим ЗОЗ с позиции высот:
    zoz_high_dict = {}
    for point in eval_points:
        if is_float(point.high) and int(point.high) > 2:
            if not point.high in zoz_high_dict:
                zoz_high_dict[point.high] = point
            else:
                if is_float(point.value):
                    try:
                        if float(point.value) > float(zoz_high_dict[point.high].value):
                            zoz_high_dict[point.high] = point
                    except:
                        zoz_high_dict[point.high] = point

    if len(zoz_high_dict) > 0:
        zoz_high_point = templates.filter(item_short='zoz_high_point').first().item_long
        zoz_description += '\nПри оценке ЗОЗ для существующей застройки были исследованы следующие контрольные точки:'
        for point_key in zoz_high_dict:
            zoz_description += zoz_high_point.replace('#PLAN_NO', str(zoz_high_dict[point_key].no_plan)).replace(
                '#HIGH', point_key).replace(
                '#VALUE', zoz_high_dict[point_key].value+zoz_high_dict[point_key].unit)

    # Рассмотрим ЗОЗ с позиции азимутов
    zoz_description += '\n' + templates.filter(item_short='zoz_az').first().item_long

    sd_1 = SourceData.get_az_by_kind(see_model.ref_object, 1)

    zoz_description += '\nПроектируемое оборудование:'

    az_template = templates.filter(item_short='zoz_point').first()
    for point in zoz_points:
        if point.az in sd_1:
            zoz_description += az_template.item_long.replace('#AZ', point.az).replace(
                '#HIGH', point.high).replace(
                '#R', point.distance).replace(
                '#LOW', point.low
            )

    sd_2 = SourceData.get_az_by_kind(see_model.ref_object, 2)
    zoz_description += '\nСуществующее оборудование:'
    for point in zoz_points:
        if point.az in sd_2:
            zoz_description += az_template.item_long.replace('#AZ', point.az).replace(
                '#HIGH', point.high).replace(
                '#R', point.distance).replace(
                '#LOW', point.low
            )

    if detailed:
        # sd_3_az = SourceData.get_az_by_kind(see_model.ref_object, 3)
        sd_3 = SourceData.objects.filter(ref_object=see_model.ref_object).filter(kind_code=3).order_by('ref_owner')
        if sd_3:
            zoz_description += '\nСтороннее оборудование:'
            rows = groupby(sd_3, key=attrgetter('ref_owner'))
            for title, items in rows:
                zoz_description += '\n'+title.short_name+':'
                sd_3_az = SourceData.get_az_by_kind_owner(see_model.ref_object, 3, title)
                for point in zoz_points:
                    if point.az in sd_3_az:
                        zoz_description += az_template.item_long.replace('#AZ', point.az).replace(
                            '#HIGH', point.high).replace(
                            '#R', point.distance).replace(
                            '#LOW', point.low
                        )

    zoz_description += '\n'+templates.filter(item_short='zoz_final').first().item_long

    return JsonResponse({'szz': szz_description, 'zoz': zoz_description})


def generate_ez_zones(request):
    szz = request.GET['szz']
    low = request.GET['low']
    if not low:
        low = '-'
    detailed = request.GET['detailed']
    ez_model = get_object_or_404(EZ, ez_id=request.GET['ez_id'])
    protocol = Protocol.objects.get(ref_object=ez_model.ref_object)
    points = ProtocolPoints.get_points_by_protocol(protocol)

    templates = UniBook2.get_objects_by_category('ez_zones')

    max_value = 0
    max_value_zoz = 0
    max_value_str = 'менее 0.3(мкВт/см2)'
    max_value_str_zoz = 'менее 0.3(мкВт/см2)'
    pdu = '10(мкВт/см2)'
    pdu_zoz = '10(мкВт/см2)'
    szz_points = []
    zoz_points = []
    zoz_high = []
    for point in points:
        try:
            high = int(point.high)
            if high == 2:
                szz_points.append(point.no)
                if is_float(point.value):
                    float_value = floatFloor(float(point.value), 2)
                    if float_value > max_value:
                        max_value = float_value
                        max_value_str = point.value+'('+point.unit+')'
                        pdu = point.pdu+'('+point.unit+')'
            elif high > 2:
                zoz_points.append(point.no)
                zoz_high.append(point.high)
                if is_float(point.value):
                    float_value = floatFloor(float(point.value), 2)
                    if float_value > max_value_zoz:
                        max_value_zoz = float_value
                        max_value_str_zoz = point.value+'('+point.unit+')'
                        pdu_zoz = point.pdu+'('+point.unit+')'
        except:
            pass

    list_set = set(zoz_high)
    zoz_high = list(list_set)
    zoz_high_h_list = ['H='+x+'м' for x in zoz_high]

    szz_description = templates.filter(item_short='szz').first()
    szz_description = szz_description.item_long.replace('#proto_no', protocol.protocol_no).replace(
                                                        '#proto_date', protocol.protocol_date.strftime('%d.%m.%Y')).replace(
                                                        '#szz_point', str(szz_points)).replace(
                                                        '#max_value', max_value_str).replace(
                                                        '#pdu', pdu)

    zoz_description = templates.filter(item_short='zoz_start').first()
    zoz_description = zoz_description.item_long.replace('#proto_no', protocol.protocol_no).replace(
                                                        '#proto_date', protocol.protocol_date.strftime('%d.%m.%Y')).replace(
                                                        '#pp', str(zoz_points)).replace(
                                                        '#high', ', '.join(zoz_high_h_list)).replace(
                                                        '#max', max_value_str_zoz).replace(
                                                        '#pdu', pdu_zoz).replace('#low', low)

    see_model = SEE.objects.get(ref_object=ez_model.ref_object)
    if see_model:
        see_model = see_model
        zoz_description += '\nНа высоте максимумом излучений в горизонтальной плоскости установлено:'
        zoz_points = ZoneByPoints.get_zone_by_see(see_model)

        type_1 = zoz_points.filter(point_type=1)
        zoz_description += '\nПроектируемое оборудование:'

        az_template = templates.filter(item_short='zoz_point').first()
        for point in type_1:
            zoz_description += az_template.item_long.replace('#AZ', point.az).replace(
                '#HIGH', point.high).replace(
                '#R', point.distance)

        type_2 = zoz_points.filter(point_type=2)
        zoz_description += '\nСуществующее оборудование:'
        for point in type_2:
            zoz_description += az_template.item_long.replace('#AZ', point.az).replace(
                '#HIGH', point.high).replace(
                '#R', point.distance)

        if detailed:
            type_3 = zoz_points.filter(point_type=3)
            zoz_description += '\nСтороннее оборудование:'
            for point in type_3:
                zoz_description += az_template.item_long.replace('#AZ', point.az).replace(
                    '#HIGH', point.high).replace(
                    '#R', point.distance)

    return JsonResponse({'szz': szz_description, 'zoz': zoz_description})


DOCUMENT_TYPES_DICT = {
    'oos': 'Приложения к СЭЗ',
    'see': 'Санитарно-эпидемиологическая экспертиза',
    'protocol': 'Протокол измерений ЭМП',
    'ez': 'Экспертное заключение на протокол'
}


def load_ref_low(request):
    context = {
        'doc_types': DOCUMENT_TYPES_DICT,
        'evals': UniBook2.get_objects_by_category('evaluation_low'),
        'methods': UniBook2.get_objects_by_category('method_low')
    }

    return render(request, 'inspection/ref_doc_low.html', context)


def load_ref_sign(request):
    context = {
        'doc_types': DOCUMENT_TYPES_DICT,
        'persons': User.objects.all(),
    }

    return render(request, 'inspection/ref_sign.html', context)


def load_sign(request):
    doc_type = request.GET['doc_type']
    context = {
        'signs': DocumentSign.get_sign_by_type(doc_type),
    }
    sign_form = DocumentSignForm(initial={
        'document_type': doc_type
    })
    context['sign_form'] = sign_form

    return render(request, 'inspection/sign_content.html', context)


def load_doc_low_content(request):
    doc_type = request.GET['doc_type']
    context = {
        'my_evals': DocumentLow.get_items_by_types(doc_type, 'evals'),
        'my_methods': DocumentLow.get_items_by_types(doc_type, 'methods')
    }

    return render(request, 'inspection/doc_low.html', context)


def delete_doc_low(request):
    doc_type = request.GET['doc_type']
    doc_id = request.GET['doc_id']
    doc_low = get_object_or_404(DocumentLow, id=doc_id)
    doc_low.delete()

    context = {
        'my_evals': DocumentLow.get_items_by_types(doc_type, 'evals'),
        'my_methods': DocumentLow.get_items_by_types(doc_type, 'methods')
    }

    return render(request, 'inspection/doc_low.html', context)


def delete_sign(request):
    doc_type = request.GET['doc_type']
    sign_id = request.GET['sign_id']
    sign = get_object_or_404(DocumentSign, id=sign_id)
    sign.delete()

    context = {
        'signs': DocumentSign.get_sign_by_type(doc_type)
    }
    sign_form = DocumentSignForm(initial={
        'document_type': doc_type
    })
    context['sign_form'] = sign_form

    return render(request, 'inspection/sign_content.html', context)


def add_doc_low(request):
    doc_type = request.GET['doc_type']
    low_type = request.GET['low_type']
    notation = request.GET['notation']
    name = request.GET['name']

    DocumentLow.objects.create(document_type=doc_type, low_type=low_type, low_notation=notation, low_name=name)

    context = {
        'my_evals': DocumentLow.get_items_by_types(doc_type, 'evals'),
        'my_methods': DocumentLow.get_items_by_types(doc_type, 'methods')
    }

    return render(request, 'inspection/doc_low.html', context)


def doc_generation(request, ref_object):
    object_ = get_object_or_404(InspectionObject, id=ref_object)
    res_doc = ResultDocument.objects.get_or_create(ref_object=object_, document_type='see')[0]
    res_doc_protocol = ResultDocument.objects.get_or_create(ref_object=object_, document_type='protocol')[0]
    res_doc_ez = ResultDocument.objects.get_or_create(ref_object=object_, document_type='ez')[0]
    res_doc_oos = ResultDocument.objects.get_or_create(ref_object=object_, document_type='oos')[0]
    gen_form_see = ResultDocumentForm(instance=res_doc)
    gen_form_protocol = ResultDocumentForm(instance=res_doc_protocol)
    gen_form_ez = ResultDocumentForm(instance=res_doc_ez)
    gen_form_oos = ResultDocumentForm(instance=res_doc_oos)
    context = {
        'object': object_,
        'res_doc': res_doc,
        'res_doc_protocol': res_doc_protocol,
        'res_doc_ez': res_doc_ez,
        'res_doc_oos': res_doc_oos,
        'gen_form_see': gen_form_see,
        'gen_form_protocol': gen_form_protocol,
        'gen_form_ez': gen_form_ez,
        'gen_form_oos': gen_form_oos,
    }

    return render(request, 'inspection/doc_generation.html', context)


def generate_doc(request, doc_type, ref_object):
    if doc_type == 'see':
        return generate(get_object_or_404(InspectionObject, id=ref_object))
    elif doc_type == 'protocol':
        return generate_protocol(get_object_or_404(InspectionObject, id=ref_object))
    elif doc_type == 'ez':
        return generate_ez(get_object_or_404(InspectionObject, id=ref_object))
    elif doc_type == 'oos':
        return generate_oos(get_object_or_404(InspectionObject, id=ref_object))


def download_doc(request, doc_type, ref_object):
    pass


def gen_see_post(request):
    context = {}
    if request.method == 'POST':
        res_doc_id = request.POST['id']
        res_doc = get_object_or_404(ResultDocument, id=res_doc_id)
        form = ResultDocumentForm(request.POST, request.FILES, instance=res_doc)
        if form.is_valid():
            post = form.save()
            post.refresh_from_db()

            if request.FILES.get('attach_word', None):
                res_convert = ms_word_to_pdf(request.FILES['attach_word'])
                if res_convert['success']:
                    res_doc.attach_pdf.save(res_convert['file_path']+'.pdf',
                                            File(default_storage.open(res_convert['file_path']+'.pdf')),
                                            save=True)
                    print(res_convert)
                    default_storage.delete(res_convert['file_path'])
                    default_storage.delete(res_convert['file_path']+'.pdf')

                    res_sign = sign_doc(res_doc.attach_pdf)
                    if res_sign['success']:
                        res_doc.pdf_signed.save(res_sign['out_file_name'],
                                                File(default_storage.open(res_sign['out_file'])),
                                                save=True)
                        default_storage.delete(res_sign['out_file'])
                        if form.is_valid():
                            form.save()
                            context = {
                                'res_doc': res_doc
                            }

                            # Здесь необходимо обновить объект Card
                            see_obj = SEE.objects.filter(ref_object=res_doc.ref_object).first()
                            if see_obj:
                                obj = see_obj
                            else:
                                obj = res_doc
                            new_card = link_to_order('see', obj)
                            if new_card['success']:
                                if new_card['obj']:
                                    new_card['obj'].source_file = res_doc.attach_word
                                    new_card['obj'].archive_file = res_doc.pdf_signed
                                    new_card['obj'].save()
                                context['success'] = new_card['msg']
                            else:
                                context['error'] = new_card['msg']

    return render(request, 'inspection/extra_gen_doc.html', context)


def gen_oos_post(request):
    context = {}
    if request.method == 'POST':
        res_doc_id = request.POST['id']
        res_doc = get_object_or_404(ResultDocument, id=res_doc_id)
        form = ResultDocumentForm(request.POST, request.FILES, instance=res_doc)
        if form.is_valid():
            post = form.save()
            post.refresh_from_db()

            if request.FILES.get('attach_word', None):
                res_convert = ms_word_to_pdf(request.FILES['attach_word'])
                if res_convert['success']:
                    res_doc.attach_pdf.save(res_convert['file_path']+'.pdf',
                                            File(default_storage.open(res_convert['file_path']+'.pdf')),
                                            save=True)
                    print(res_convert)
                    default_storage.delete(res_convert['file_path'])
                    default_storage.delete(res_convert['file_path']+'.pdf')

                    res_sign = sign_doc(post.pdf_signed)
                    if res_sign['success']:
                        res_doc.pdf_signed.save(res_sign['out_file_name'],
                                                File(default_storage.open(res_sign['out_file'])),
                                                save=True)
                        default_storage.delete(res_sign['out_file'])
                        if form.is_valid():
                            form.save()
                            context = {
                                'res_doc_oos': res_doc
                            }

                            # Здесь необходимо обновить объект Card
                            new_card = link_to_order('oos', res_doc)
                            if new_card['success']:
                                if new_card['obj']:
                                    new_card['obj'].source_file = res_doc.attach_word
                                    new_card['obj'].archive_file = res_doc.pdf_signed
                                    new_card['obj'].save()
                                context['success'] = new_card['msg']
                            else:
                                context['error'] = new_card['msg']

    return render(request, 'inspection/extra_gen_doc_oos.html', context)


def gen_ez_post(request):
    context = {}
    if request.method == 'POST':
        res_doc_id = request.POST['id']
        res_doc = get_object_or_404(ResultDocument, id=res_doc_id)
        form = ResultDocumentForm(request.POST, request.FILES, instance=res_doc)
        if request.FILES.get('attach_word', None):
            res_convert = ms_word_to_pdf(request.FILES['attach_word'])
            if res_convert['success']:
                res_doc.attach_pdf.save(res_convert['file_path']+'.pdf',
                                        File(default_storage.open(res_convert['file_path']+'.pdf')),
                                        save=True)
                print(res_convert)
                default_storage.delete(res_convert['file_path'])
                default_storage.delete(res_convert['file_path']+'.pdf')

                res_sign = sign_doc(res_doc.attach_pdf)
                if res_sign['success']:
                    res_doc.pdf_signed.save(res_sign['out_file_name'],
                                            File(default_storage.open(res_sign['out_file'])),
                                            save=True)
                    default_storage.delete(res_sign['out_file'])
                    if form.is_valid():
                        form.save()
                        context = {
                            'res_doc_ez': res_doc
                        }

                        # Здесь необходимо обновить объект Card
                        ez_obj = EZ.objects.filter(ref_object=res_doc.ref_object).first()
                        if ez_obj:
                            obj = ez_obj
                        else:
                            obj = res_doc
                        new_card = link_to_order('ez', obj)
                        if new_card['success']:
                            if new_card['obj']:
                                new_card['obj'].source_file = res_doc.attach_word
                                new_card['obj'].archive_file = res_doc.pdf_signed
                                new_card['obj'].save()
                            context['success'] = new_card['msg']
                        else:
                            context['error'] = new_card['msg']

    return render(request, 'inspection/extra_gen_doc_ez.html', context)


def gen_protocol_post(request):
    context = {}
    if request.method == 'POST':
        res_doc_id = request.POST['id']
        res_doc = get_object_or_404(ResultDocument, id=res_doc_id)
        form = ResultDocumentForm(request.POST, request.FILES, instance=res_doc)
        if request.FILES.get('attach_word', None):
            res_convert = ms_word_to_pdf(request.FILES['attach_word'])
            if res_convert['success']:
                res_doc.attach_pdf.save(res_convert['file_path']+'.pdf',
                                        File(default_storage.open(res_convert['file_path']+'.pdf')),
                                        save=True)
                print(res_convert)
                default_storage.delete(res_convert['file_path'])
                default_storage.delete(res_convert['file_path']+'.pdf')

                res_sign = sign_doc(res_doc.attach_pdf)
                if res_sign['success']:
                    res_doc.pdf_signed.save(res_sign['out_file_name'],
                                            File(default_storage.open(res_sign['out_file'])),
                                            save=True)
                    default_storage.delete(res_sign['out_file'])
                    if form.is_valid():
                        form.save()
                        context = {
                            'res_doc_protocol': res_doc
                        }

                        # Здесь необходимо обновить объект Card
                        protocol_obj = Protocol.objects.filter(ref_object=res_doc.ref_object).first()
                        if protocol_obj:
                            obj = protocol_obj
                        else:
                            obj = res_doc
                        new_card = link_to_order('protocol', obj)
                        if new_card['success']:
                            if new_card['obj']:
                                new_card['obj'].source_file = res_doc.attach_word
                                new_card['obj'].archive_file = res_doc.pdf_signed
                                new_card['obj'].save()
                            context['success'] = new_card['msg']
                        else:
                            context['error'] = new_card['msg']

    return render(request, 'inspection/extra_gen_doc_protocol.html', context)
