from django.shortcuts import render, get_object_or_404

from orders.models import Task, ExecutionPlan
from .models import Pribor
from .forms import PriborForm
from django.db.models import Q
from references.models import UniBook2
from django.http import HttpResponseRedirect
from django.urls import reverse
from int_messages.service import new_alert, mark_alert_as_red
from inspection.models import Protocol
from laboratory.models import ProtocolPribor
from django.contrib.auth.decorators import permission_required

# Create your views here.

@permission_required('accounts.can_view_laboratory')
def source_table(request):
    plans = ExecutionPlan.objects.filter(int_executor=request.user.profile.department).filter(
                                         ref_task__ref_order__close_date__isnull=True).exclude(
                                         ref_task__accept_date__isnull=True)

    tasks = []
    for ep in plans:
        tasks.append(ep.ref_task)

    orders = []
    for task in tasks:
        if task.ref_order not in orders:
            if not task.ref_order.close_date:
                orders.append(task.ref_order)

    return render(request, 'laboratory/order_list.html', {'orders': orders})

@permission_required('accounts.can_view_laboratory')
def pribor_list(request, success=None):
    if success:
        context = {'success': success}
    else:
        context = {}
    pribors = Pribor.objects.all().order_by('category')
    context['pribors'] = pribors

    return render(request, 'laboratory/pribor_list.html', context)


@permission_required('accounts.can_view_laboratory')
def pribor_warn_list(request, success=None):
    if success:
        context = {'success': success}
    else:
        context = {}
    pribors = Pribor.get_expired()
    context['pribors'] = pribors
    mark_alert_as_red(310, request.user.profile.department)

    return render(request, 'laboratory/pribor_warn_list.html', context)


def ajax_pribor_list(request):
    search_line = request.GET['search_line']
    if search_line:
        pribors = Pribor.objects.filter(
            Q(name__icontains=search_line) |
            Q(purpose__icontains=search_line) |
            Q(certificate_place__icontains=search_line))[:50]
    else:
        pribors = Pribor.objects.all()[:50]
    context = {
        'pribors': pribors,
    }
    return render(request, 'laboratory/pribor_list_ajax.html', context)


@permission_required('accounts.can_manage_devices')
def pribor_detail(request, pribor_id):
    pribor = get_object_or_404(Pribor, id=pribor_id)
    pribor_form = PriborForm(instance=pribor)
    categories = UniBook2.get_objects_by_category('pribor_category')
    context = {
        'pribor': pribor,
        'form': pribor_form,
        'categories': categories
    }
    return render(request, 'laboratory/pribor_detail.html', context)


@permission_required('accounts.can_manage_devices')
def pribor_save(request):
    context = {}
    if request.method == 'POST':
        pribor_form = PriborForm(request.POST, request.FILES, instance=Pribor.objects.get(pk=request.POST['id']))
        if pribor_form.is_valid():
            pribor_form.save()
            context = {
                'success': 'Сведения об оборудовании отредактированы!',
            }
            return HttpResponseRedirect(reverse('laboratory:pribor-list-success', kwargs=context))
    return render(request, 'laboratory/pribor_detail.html', context)


@permission_required('accounts.can_manage_devices')
def pribor_create(request):
    categories = UniBook2.get_objects_by_category('pribor_category')
    if request.method == 'POST':
        form = PriborForm(request.POST)
        if form.is_valid():
            pre_form = form.save()
            context = {
                'success': 'Сведения были успешно добавлены!',
            }
            pre_form.refresh_from_db()
            pribor_obj = get_object_or_404(Pribor, id=pre_form.pk)
            alert_context = {
                'alert_code': 300,
                'action_url': pribor_obj.get_absolute_url(),
                'position': None,
                'department': request.user.profile.department,
                'topic': 'Создана новая запись о Приборе (оборудовании):'+pribor_obj.name,
                'body':  'Добавлен Прибор (Оборудование): '+pribor_obj.name+'. Категория: '+pribor_obj.category,
            }
            status = new_alert(alert_context)
            print('Alert status:', status)
            return HttpResponseRedirect(reverse('laboratory:pribor-list-success', kwargs=context))
    else:
        form = PriborForm()
    context = {
        'form': form,
        'categories': categories
    }
    return render(request, 'laboratory/pribor_create.html', context)


@permission_required('accounts.can_manage_devices')
def pribor_delete(request, pribor_id):
    pribor_obj = get_object_or_404(Pribor, id=pribor_id)
    pribor_name = pribor_obj.name
    pribor_obj.delete()
    context = {
        'success': 'Прибор (Оборудование) ' + pribor_name + ' был успешно удален!',
    }
    return HttpResponseRedirect(reverse('laboratory:pribor-list-success', kwargs=context))


def ref_protocol_emp(request):
    context = {
        'pribors': Pribor.get_data_by_status('active'),
        'protocol_pribors': ProtocolPribor.get_data_by_kind(0),
    }

    return render(request, 'laboratory/ref_protocol_emp.html', context)


@permission_required('site_administrator')
def add_pribor_ref(request):
    pribor_id = request.GET['pribor_id']
    pribor = get_object_or_404(Pribor, id=pribor_id)
    protocol_pribor = ProtocolPribor.objects.create(ref_pribor=pribor, kind=0)

    data = {
        'protocol_pribors': ProtocolPribor.get_data_by_kind(0),
    }

    return render(request, 'laboratory/pribors_table.html', data)


@permission_required('site_administrator')
def delete_pribor(request):
    pribor_id = request.GET['pribor_id']
    pribor = get_object_or_404(ProtocolPribor, id=pribor_id)
    pribor.delete()

    data = {
        'protocol_pribors': ProtocolPribor.get_data_by_kind(0),
    }

    return render(request, 'laboratory/pribors_table.html', data)