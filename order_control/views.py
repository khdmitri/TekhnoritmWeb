from django.shortcuts import render, get_object_or_404, redirect
from references.models import DefaultTasks, Region
from accounts.models import Profile, Department
from .models import ControlConfig, AlertPersonality
from orders.models import Task, ExecutionPlan, TARGET_DOC_DICT, Card
from .forms import ControlConfigForm, StandardRequestForm
from django.db.models import Q
from functools import reduce
from operator import and_
import datetime
from accounts.choices import USER_REGION

# Create your views here.


def show_target_list(request, alert_message=None):
    tasks = DefaultTasks.objects.all().order_by('task_type', 'position')
    context = {
        'tasks': tasks,
        'alert_message': alert_message,
    }
    return render(request, 'order_control/target_list.html', context)


def control_config(request, task_id):
    task = get_object_or_404(DefaultTasks, id=task_id)
    control_card = ControlConfig.get_object_by_task(task)
    alert_message = None
    if request.method == 'POST':
        form = ControlConfigForm(request.POST, instance=control_card)
        if form.is_valid():
            form.save()
            alert_message = 'Настройки контроля задачи были успешно обновлены!'
    else:
        if not control_card:
            control_card = ControlConfig.objects.create(ref_task=task)
            control_card.save()
    form = ControlConfigForm(instance=control_card)
    persons = Profile.objects.filter(~Q(position='Не_определено')).filter(is_new=False)
    person_list = AlertPersonality.objects.filter(ref_task=control_card)

    context = {
        'control_card': control_card,
        'persons': persons,
        'person_list': person_list,
        'form': form,
        'alert_message': alert_message,
        'task_id': task.id,
    }

    return render(request, 'order_control/config_card.html', context)


def add_person_to_alert(request):
    task_id = request.GET['task_id']
    person_id = request.GET['person_id']
    task = get_object_or_404(ControlConfig, id=task_id)
    person = get_object_or_404(Profile, id=person_id)

    if_exist = AlertPersonality.objects.filter(ref_task=task, ref_profile=person)
    if not if_exist:
        new_alert = AlertPersonality.objects.create(ref_task=task, ref_profile=person)
        new_alert.save()

    persons = Profile.objects.filter(~Q(position='Не_определено')).filter(is_new=False)
    person_list = AlertPersonality.objects.filter(ref_task=task)
    context = {
        'persons': persons,
        'person_list': person_list,
    }

    return render(request, 'order_control/persons_to_alert.html', context)


def delete_person(request):
    ap_id = request.GET['alert_personality_id']
    ap = get_object_or_404(AlertPersonality, id=ap_id)
    task = ap.ref_task

    ap.delete()

    persons = Profile.objects.filter(~Q(position='Не_определено')).filter(is_new=False)
    person_list = AlertPersonality.objects.filter(ref_task=task)
    context = {
        'persons': persons,
        'person_list': person_list,
    }

    return render(request, 'order_control/persons_to_alert.html', context)


def delete_card(request, card_id):
    cc = get_object_or_404(ControlConfig, id=card_id)
    task_target = cc.ref_task.target
    cc.delete()
    return redirect('order_control:target-list-alert', alert_message='Контроль задачи '+task_target+' был успешно удален!')


def control_list(request):
    return render(request, 'order_control/control_list.html')


def control_division(request):
    context = {}
    if request.method == 'POST':
        form = StandardRequestForm(request.POST)
        if form.is_valid():
            sq = Task.objects.filter(accept_date__isnull=False).filter(close_date__isnull=True)
            if form.cleaned_data['use_region']:
                if form.cleaned_data['region']:
                    selected_region = get_object_or_404(Region, id=form.cleaned_data['region'])
                    sq = sq.filter(ref_order__region=selected_region.short_name)
                    context['selected_region'] = selected_region
            if form.cleaned_data['only_warning']:
                now = datetime.date.today()
                warn_date = now + datetime.timedelta(days=7)
                sq = sq.filter(dead_line__lte=warn_date)
            results = sq.order_by('dead_line')
            context['results'] = results
            context['form'] = form
    else:
        context = {
            'form': StandardRequestForm(initial={
                'use_region': False,
                'only_warning': False
            }),
        }

    context['regions'] = Region.objects.all()

    return render(request, 'order_control/control_division.html', context)


def control_kind(request):
    context = {}
    if request.method == 'POST':
        form = StandardRequestForm(request.POST)
        if form.is_valid():
            sq = ExecutionPlan.objects.filter(start_date__isnull=False).filter(stop_date__isnull=True)
            cc = None
            if form.cleaned_data['use_region']:
                if form.cleaned_data['region']:
                    selected_region = get_object_or_404(Region, id=form.cleaned_data['region'])
                    sq = sq.filter(ref_task__ref_order__region=selected_region.short_name)
                    context['selected_region'] = selected_region
            if form.cleaned_data['target']:
                dt = DefaultTasks.objects.filter(id=form.cleaned_data['target']).first()
                cc = ControlConfig.get_object_by_task(dt)
                context['selected_target'] = dt
                if dt:
                    sq = sq.filter(target=dt.target).filter(ref_task__task_type=dt.task_type)
            if form.cleaned_data['only_warning']:
                if cc is not None:
                    sq = sq.filter(start_date__lte=datetime.date.today()-datetime.timedelta(days=cc.warn_days))
            results = sq.order_by('start_date')
            context['results'] = results
            context['form'] = form
    else:
        context = {
            'form': StandardRequestForm(initial={
                'use_region': False,
            }),
        }

    context['regions'] = Region.objects.all()
    tasks = DefaultTasks.objects.all().order_by('task_type', 'position')
    context['tasks'] = tasks

    return render(request, 'order_control/control_kind.html', context)


def control_card(request):
    context = {
        'regions': USER_REGION,
        'form': StandardRequestForm(),
    }
    return render(request, 'order_control/control_card.html', context)


def ajax_search_card(request):
    search_line = request.GET['search_line']
    type_search = request.GET['type_search']
    region = request.GET['region']
    if search_line:
        region_qs = None
        if region != '0':
            region_qs = reduce(and_, (Q(ref_action__ref_task__ref_order__region=region),))
        if type_search == 'strong':
            if region_qs is not None:
                cards = Card.objects.filter(Q(object_full_name__icontains=search_line) | Q(
                    doc_title__icontains=search_line)).filter(region_qs).order_by(
                    '-start_date')[:20]
            else:
                cards = Card.objects.filter(Q(object_full_name__icontains=search_line) | Q(
                    doc_title__icontains=search_line)).order_by(
                    '-start_date')[:20]
        else:
            ofn_qs = reduce(and_, (Q(object_full_name__icontains=x) for x in search_line.split()))
            dt_qs = reduce(and_, (Q(doc_title__icontains=x) for x in search_line.split()))
            db_qs = reduce(and_, (Q(doc_base__icontains=x) for x in search_line.split()))
            if region_qs is not None:
                cards = Card.objects.filter(ofn_qs | dt_qs | db_qs).filter(region_qs).order_by('-start_date')[:20]
            else:
                cards = Card.objects.filter(ofn_qs | dt_qs | db_qs).order_by('-start_date')[:20]

    else:
        cards = None
    context = {
        'cards': cards,
        'regions': USER_REGION,
    }
    return render(request, 'order_control/card_list_ajax.html', context)


def kind_objects(request, action_id):
    action = get_object_or_404(ExecutionPlan, id=action_id)
    cards = Card.get_cards_by_action(action)

    context = {
        'action': action,
        'cards': cards,
    }

    return render(request, 'order_control/cards.html', context)


EXT_EXECUTORS_DICT = {
    'RPN': 'Роспотребнадзор',
    'FMBA': 'ФМБА',
    'OWNER': 'Владелец ПРТО',
    'CLIENT': 'Заказчик',
    'OTHER': 'Иное',
}


def control_executor(request):
    context = {}
    if request.method == 'POST':
        form = StandardRequestForm(request.POST)
        if form.is_valid():
            sq = ExecutionPlan.objects.filter(start_date__isnull=False).filter(stop_date__isnull=True)
            if form.cleaned_data['use_region']:
                if form.cleaned_data['region']:
                    selected_region = get_object_or_404(Region, id=form.cleaned_data['region'])
                    sq = sq.filter(ref_task__ref_order__region=selected_region.short_name)
                    context['selected_region'] = selected_region
            if form.cleaned_data['executor']:
                context['selected_executor'] = form.cleaned_data['executor']
                if form.cleaned_data['executor'] == 1:
                    dep = get_object_or_404(Department, name=form.cleaned_data['int_executor'])
                    context['selected_int'] = dep
                    sq = sq.filter(int_executor=dep)
                elif form.cleaned_data['executor'] == 2:
                    context['selected_ext_key'] = form.cleaned_data['ext_executor']
                    context['selected_ext_value'] = EXT_EXECUTORS_DICT[form.cleaned_data['ext_executor']]
                    sq = sq.filter(ext_executor=form.cleaned_data['ext_executor'])
            results = sq.order_by('start_date')
            context['results'] = results
            context['form'] = form
    else:
        context = {
            'form': StandardRequestForm(initial={
                'use_region': False,
            }),
        }

    context['regions'] = Region.objects.all()
    int_executors = Department.objects.all().order_by('name')
    ext_executors = EXT_EXECUTORS_DICT

    context['int_executors'] = int_executors
    context['ext_executors'] = ext_executors

    return render(request, 'order_control/control_executor.html', context)