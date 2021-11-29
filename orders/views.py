from django.shortcuts import render, get_object_or_404
from .models import Order, Task, ExecutionPlan, Card
from django.db.models import Q
from .forms import OrderForm, OrderCreateForm, OrderTaskForm, OrderTaskEditForm, ExecutionPlanForm, ExecutionCardForm
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from references.models import Client, DefaultTasks, Contract
from int_messages.service import new_alert, mark_alert_as_red
from accounts.models import Department
from django.contrib.auth.decorators import permission_required
from .service import generate_sez_request, generate_letter_request, get_title_from_parent
from .tasks import make_archive
from generators.service import get_new_value
from orders.tasks import my_task

# Create your views here.

TYPE_TO_DEPARTMENT = {
    'R1': 'Орган инспекции',
    'R2': 'Орган инспекции',
    'PK-PRTO': 'Орган инспекции',
    'PK': 'Испытательная лаборатория',
    'SOUT': 'СОУТ',
    'OTHER': 'АХО (Администрация)',
}


def order_list(request, success=None):
    if success:
        context = {'success': success}
    else:
        context = {}
    orders = Order.objects.all()
    context['orders'] = orders

    return render(request, 'orders/order_list.html', context)


def ajax_order_list(request):
    search_line = request.GET['search_line']
    if search_line:
        orders = Order.objects.filter(
            Q(order_id__icontains=search_line) |
            Q(description__icontains=search_line)).exclude(
            close_date__isnull=False)[:20]
    else:
        orders = Order.objects.all().exclude(close_date__isnull=False)[:20]
    context = {
        'orders': orders,
    }
    return render(request, 'orders/order_list_ajax.html', context)


def ajax_control_order_search(request):
    search_line = request.GET['search_line']
    if search_line:
        orders = Order.objects.filter(
            Q(order_id__icontains=search_line) |
            Q(description__icontains=search_line) |
            Q(client__short_name__icontains=search_line) |
            Q(client__long_name__icontains=search_line) |
            Q(client__representative__icontains=search_line))[:20]
    else:
        orders = Order.objects.all().exclude(close_date__isnull=False)[:20]
    context = {
        'orders': orders,
    }
    return render(request, 'orders/control_order_tab.html', context)


def ajax_control_task_search(request):
    search_line = request.GET['search_line']
    if search_line:
        tasks = Task.objects.filter(
            Q(task_id__icontains=search_line) |
            Q(description__icontains=search_line) |
            Q(task_type__icontains=search_line) |
            Q(distribution_dep__name__icontains=search_line) |
            Q(distribution_dep__description__icontains=search_line))[:20]
    else:
        tasks = None
    context = {
        'tasks': tasks,
    }
    return render(request, 'orders/control_task_tab.html', context)


def ajax_control_action_search(request):
    search_line = request.GET['search_line']
    if search_line:
        actions = ExecutionPlan.objects.filter(
            Q(int_executor__description__icontains=search_line) |
            Q(target__icontains=search_line) |
            Q(ext_executor__icontains=search_line))[:20]
    else:
        actions = None
    context = {
        'actions': actions,
    }
    return render(request, 'orders/control_action_tab.html', context)


def ajax_control_card_search(request):
    search_line = request.GET['search_line']
    if search_line:
        cards = Card.objects.filter(
            Q(doc_no__icontains=search_line) |
            Q(doc_type__icontains=search_line) |
            Q(doc_title__icontains=search_line))[:20]
    else:
        cards = None
    context = {
        'cards': cards,
    }
    return render(request, 'orders/control_card_tab.html', context)


def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order_form = OrderForm(instance=order)
    context = {
        'order': order,
        'form': order_form,
        'contracts': order.client.get_available_contracts(),
        'order_contracts': order.contracts.all()
    }
    return render(request, 'orders/order_detail.html', context)


def order_create(request):
    if request.method == 'POST':
        form = OrderCreateForm(request.POST, request.FILES)
        if form.is_valid():
            pre_form = form.save(commit=False)
            client_id = form.cleaned_data.get('client_id')
            client_obj = get_object_or_404(Client, id=client_id)
            pre_form.client = client_obj
            pre_form.img = form.cleaned_data['img']
            service_order = get_object_or_404(Order, order_id='service')
            pre_form.contracts.set(service_order.contracts.all())
            pre_form.save()
            service_order.contracts.clear()
            pre_form.refresh_from_db()
            context = {
                'success': 'Заявка была успешно добавлена!',
            }
            order_obj = get_object_or_404(Order, order_id=pre_form.pk)
            alert_context = {
                'alert_code': 100,
                'action_url': order_obj.get_absolute_url(),
                'position': None,
                'department': request.user.profile.department,
                'topic': 'Создана заявка №'+order_obj.order_id,
                'body':  'После создания заявки требуется детализация по исполнению работ по подразделениям внутри '
                         'организации, либо отправка на рассмотрение в органы государственной власти',
            }
            status = new_alert(alert_context)
            print('Alert status:', status)
            return HttpResponseRedirect(reverse('orders:order-list-success', kwargs=context))
    else:
        form = OrderCreateForm()
        service_order = get_object_or_404(Order, order_id='service')
        service_order.contracts.clear()
    return render(request, 'orders/order_create.html', {'form': form})


def order_save(request):
    order = get_object_or_404(Order, order_id=request.POST['order_id'])
    context = {'order': order}
    if request.method == 'POST':
        order_form = OrderForm(request.POST, request.FILES, instance=order)
        if order_form.is_valid():
            order_form.save()
            context = {
                'success': 'Заявка была успешно отредактирована!',
            }
            return HttpResponseRedirect(reverse('orders:order-list-success', kwargs=context))
        else:
            context = {
                'order': order,
                'form': order_form
            }
    return render(request, 'orders/order_detail.html', context)


def order_task_create(request, ref_order):
    if request.method == 'POST':
        form = OrderTaskForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            post.refresh_from_db()
            context = {
                'task_id': form.cleaned_data['task_id']
            }
            return HttpResponseRedirect(reverse('orders:order-task-detail', kwargs=context))
    else:
        form = OrderTaskForm(initial={'ref_order': ref_order})
    return render(request, 'orders/order_task_create.html', {'form': form, 'ref_order': ref_order})


def order_task_detail(request, task_id):
    obj = get_object_or_404(Task, task_id=task_id)
    success = None
    if request.method == 'POST':
        edit_form = OrderTaskEditForm(request.POST, request.FILES, instance=obj)
        if edit_form.is_valid():
            edit_form.save()
            success = 'Тип работы по заявке был успешно отредактирован!'
    else:
        edit_form = OrderTaskEditForm(instance=obj)

    context = {
        'task_obj': obj,
        'task_id': obj.task_id,
        'order_id': obj.ref_order.order_id,
        'department': TYPE_TO_DEPARTMENT[obj.task_type],
        'form': edit_form,
    }
    if success:
        context['success'] = success
    return render(request, 'orders/order_task_detail.html', context)


def ajax_search_list(request):
    search_line = request.GET['search_line']
    if search_line:
        clients = Client.objects.filter(Q(short_name__icontains=search_line) | Q(long_name__icontains=search_line))[:20]
    else:
        clients = Client.objects.all()[:20]
    context = {
        'clients': clients,
    }
    return render(request, 'orders/client_list_ajax.html', context)


def order_task_table_ajax(request):
    ref_order = request.GET['ref_order']
    tasks = Task.objects.filter(ref_order=ref_order)
    context = {
        'tasks': tasks
    }

    return render(request, 'orders/order_task_table_html.html', context)


def order_close(request, order_id):
    order_obj = get_object_or_404(Order, order_id=order_id)
    order_obj.close_date = datetime.datetime.now()
    order_obj.save()
    context = {
        'success': 'Заявка '+order_obj.order_id+' была успешно закрыта!',
    }
    return HttpResponseRedirect(reverse('orders:order-list-success', kwargs=context))


def order_delete(request, order_id):
    order_obj = get_object_or_404(Order, order_id=order_id)
    order_id = order_obj.order_id
    order_obj.delete()
    context = {
        'success': 'Заявка ' + order_id + ' была успешно удалена!',
    }
    return HttpResponseRedirect(reverse('orders:order-list-success', kwargs=context))


def order_task_close(request, task_id):
    task_obj = get_object_or_404(Task, task_id=task_id)
    task_obj.close_date = datetime.datetime.now()
    task_obj.save()
    context = {
        'task': task_obj,
    }
    return render(request, 'orders/order_task_closed.html', context)


def order_task_delete(request, task_id):
    task_obj = get_object_or_404(Task, task_id=task_id)
    context = {
        'order_id': task_obj.ref_order,
        'task_id': task_obj.task_id
    }
    task_obj.delete()

    return render(request, 'orders/order_task_deleted.html', context)


def order_publicate_ajax(request):
    ref_order = request.GET['order_id']
    action = request.GET['action']
    order = get_object_or_404(Order, order_id=ref_order)
    tasks = Task.objects.filter(ref_order=ref_order)
    if action == 'publicate':
        order.is_public = True
        order.save()
        for task in tasks:
            department_code = task.task_type
            department = get_object_or_404(Department, name=TYPE_TO_DEPARTMENT[department_code])
            task.distribution_dep = department
            task.save()
            alert_context = {
                'alert_code': 110,
                'action_url': task.get_absolute_url(),
                'position': None,
                'department': department,
                'topic': 'Создана внутренняя заявка №' + task.task_id,
                'body': 'После создания внутренней заявки требуется детализация по работам внутри подразделения '
                        'организации',
            }
            status = new_alert(alert_context)
            print('Alert status is', status)
    context = {
        'order': order,
        'tasks': tasks
    }

    return render(request, 'orders/order_publicate_ajax.html', context)


def ajax_task_action_table(request):
    task_id = request.GET['task_id']
    task = get_object_or_404(Task, task_id=task_id)
    actions = ExecutionPlan.objects.filter(ref_task=task).order_by('position')
    context = {
        'actions': actions
    }

    return render(request, 'orders/task_action_table_html.html', context)


def fill_default_actions(request):
    task_id = request.GET['task_id']
    task = get_object_or_404(Task, task_id=task_id)
    actions = ExecutionPlan.objects.filter(ref_task=task).order_by('position')
    for action in actions:
        action.delete()
    default_actions = DefaultTasks.get_obj_by_type(task.task_type)
    for action in default_actions:
        if action.start_date == 'now':
            start_date = datetime.datetime.now()
        else:
            start_date = None
        new_obj = ExecutionPlan(ref_task=task,
                                int_executor=action.int_executor,
                                ext_executor=action.ext_executor,
                                target=action.target,
                                start_date=start_date,
                                position=action.position)
        new_obj.save()
    return render(request, 'orders/done.html')


def action_create(request, task_id):
    if request.method == 'POST':
        form = ExecutionPlanForm(request.POST)
        form.ref_task = task_id
        if form.is_valid():
            post = form.save()
            post.refresh_from_db()
            context = {
                'action_id': post.pk
            }
            return HttpResponseRedirect(reverse('orders:action-detail', kwargs=context))
        else:
            context = {
                'form': form,
            }
    else:
        form = ExecutionPlanForm(initial={'ref_task': task_id})
        context = {
            'form': form,
        }
    return render(request, 'orders/action_create.html', context)


def action_detail(request, action_id):
    task_obj = get_object_or_404(ExecutionPlan, id=action_id)
    if request.method == 'POST':
        form = ExecutionPlanForm(request.POST, instance=task_obj)
        form.id = action_id
        context = {
            'action_id': action_id,
            'form': form,
        }
        if form.is_valid():
            form.save()
            context['success'] = 'Запись набора была успешно отредактирована!'
    else:
        form = ExecutionPlanForm(instance=task_obj)
        context = {
            'action_id': action_id,
            'form': form,
        }
    return render(request, 'orders/action_detail.html', context)


def action_delete(request, task_id):
    obj = get_object_or_404(ExecutionPlan, id=task_id)
    obj.delete()

    return render(request, 'orders/action_deleted.html')


@permission_required('accounts.can_distribute_job')
def distribution_list(request):
    tasks = Task.objects.filter(accept_date__isnull=True).filter(ref_order__close_date__isnull=True)
    if not request.user.is_superuser:
        if tasks:
            tasks.filter(distribution_dep=request.user.profile.department)

    return render(request, 'orders/distribution_list.html', {'tasks': tasks})


def distribute(request, task_id):
    task_obj = get_object_or_404(Task, task_id=task_id)
    context = {
        'task': task_obj
    }

    return render(request, 'orders/task_distribution.html', context)


def distribute_action(request, task_id):
    task = get_object_or_404(Task, task_id=task_id)
    task.accept_date = datetime.datetime.now()
    task.save()
    for action in ExecutionPlan.get_actions_by_task(task.task_id):
        action.is_distributed = True
        action.save()
        alert_context = {
            'alert_code': 120,
            'action_url': reverse('orders:in-process'),
            'position': None,
            'department':action.int_executor,
            'topic': 'Создана работа: ' + action.get_target_description(),
            'body': 'Следите за выполнением выданной работы. По окочании не забывайте закрывать заявку',
        }
        status = new_alert(alert_context)
    mark_alert_as_red(110, request.user.profile.department)

    return HttpResponseRedirect(reverse('orders:distribution-list'))


def in_process_list(request):
    dep = request.user.profile.department
    list_obj = ExecutionPlan.objects.filter(
        stop_date__isnull=True).filter(
        is_distributed=True).filter(
        int_executor=dep).order_by(
        'id', 'position')
    context = {
        'list_obj': list_obj
    }
    mark_alert_as_red(120, request.user.profile.department)
    return render(request, 'orders/in_process_list.html', context)


def action_execute(request, action_id):
    action = get_object_or_404(ExecutionPlan, id=action_id)
    context = {
        'action': action
    }
    return render(request, 'orders/action_execution.html', context)


def execution_list(request):
    action_id = request.GET['action_id']
    action = get_object_or_404(ExecutionPlan, id=action_id)
    executions = Card.objects.filter(ref_action=action)
    context = {
        'executions': executions
    }
    return render(request, 'orders/execution_table.html', context)


def execution_detail(request, execution_id):
    pass


def execution_post(request):
    context = {}
    if request.method == 'POST':
        if request.POST.get('execution_id', None):
            execution = get_object_or_404(Card, execution_id=request.POST['execution_id'])
            form = ExecutionCardForm(request.POST, request.FILES, instance=execution)
        else:
            form = ExecutionCardForm(request.POST, request.FILES)
        if form.is_valid():
            if form.data.get('execution_id', None):
                context = {
                    'success': 'Карта объекта была успешно отредактирована!'
                }
            else:
                context = {
                    'success': 'Карта объекта была успешно создана!'
                }
            post = form.save()
            post.refresh_from_db()
            execution = get_object_or_404(Card, execution_id=post.pk)
            context['action_id'] = form.data['ref_action']
            context['execution'] = execution
        context['form'] = form
    else:
        ref_action = request.GET['ref_action']
        action = get_object_or_404(ExecutionPlan, id=ref_action)
        execution = None
        if request.GET.get('execution_id', None):
            execution = get_object_or_404(Card, execution_id=request.GET['execution_id'])
            form = ExecutionCardForm(instance=execution)
        else:
            form = ExecutionCardForm(initial={'ref_action': action, 'doc_type': action.get_target_description})
        context = {
            'action_id': ref_action,
            'form': form
        }
        if execution:
            context['execution'] = execution
    return render(request, 'orders/execution_form.html', context)


def action_close(request, action_id):
    action = get_object_or_404(ExecutionPlan, id=action_id)
    action.stop_date = datetime.datetime.now()

    return HttpResponseRedirect(reverse('orders:in-process'))


def delete_execution(request, execution_id, action_id):
    execution = get_object_or_404(Card, execution_id=execution_id)
    execution.delete()
    context = {
        'action_id': action_id
    }
    return HttpResponseRedirect(reverse('orders:action-execute', kwargs=context))


def control_order(request):
    orders = Order.objects.filter(close_date__isnull=True)
    context = {
        'orders': orders
    }

    return render(request, 'orders/order_control.html', context)


def close_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order.close_date = datetime.date.today()
    order.save()

    # Close contract if no more links available
    contracts = order.contracts.all()
    for contract in contracts:
        orders = contract.order_set.all()
        is_closed = True
        for order in orders:
            if not order.close_date:
                is_closed = False
        if is_closed:
            contract.closed_date = datetime.date.today()
            contract.save()

    tasks = Task.get_tasks_by_order(order)
    for task in tasks:
        if not task.close_date:
            task.close_date = datetime.date.today()
            task.save()
        actions = ExecutionPlan.get_actions_by_task(task)
        for action in actions:
            if not action.stop_date:
                action.stop_date = datetime.date.today()
                action.save()

    return HttpResponseRedirect(reverse('orders:control-order'))


def close_task(request, task_id):
    task = get_object_or_404(Task, task_id=task_id)
    result = make_archive.delay(task_id)
    # result = my_task.delay(10)

    task.close_date = datetime.date.today()
    task.save()
    context = {
        'order': task.ref_order,
        'task': task,
        'actions': ExecutionPlan.get_actions_by_task(task),
        'success': True,
        'task_id': result.task_id,
        'show_progress': True
    }

    return render(request, 'orders/close_action_tab.html', context)


def close_action(request):
    action_id = request.GET['action_id']
    task_id = request.GET['task_id']
    task = get_object_or_404(Task, task_id=task_id)
    action = get_object_or_404(ExecutionPlan, id=action_id)
    action.stop_date = datetime.date.today()
    action.save()

    context = {
        'order': task.ref_order,
        'task': task,
        'actions': ExecutionPlan.get_actions_by_task(task)
    }

    return render(request, 'orders/control_action_tab.html', context)


def delete_task(request, task_id):
    task = get_object_or_404(Task, task_id=task_id)
    task.delete()

    return HttpResponseRedirect(reverse('orders:control-order'))


def delete_action(request, action_id):
    action = get_object_or_404(ExecutionPlan, id=action_id)
    action.delete()

    return HttpResponseRedirect(reverse('orders:control-order'))


def delete_card(request):
    card = get_object_or_404(Card, execution_id=request.GET['card_id'])
    card.delete()
    action_id = request.GET['action_id']
    action = get_object_or_404(ExecutionPlan, id=action_id)
    context = {
        'order': action.ref_task.ref_order,
        'task': action.ref_task,
        'action': action,
        'cards': Card.get_cards_by_action(action)
    }

    return render(request, 'orders/control_card_tab.html', context)


def delete_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order.delete()

    return HttpResponseRedirect(reverse('orders:control-order'))


def expand_order(request):
    order_id = request.GET['order_id']
    order = get_object_or_404(Order, order_id=order_id)
    context = {
        'order': order,
        'tasks': Task.get_tasks_by_order(order)
    }

    return render(request, 'orders/control_task_tab.html', context)


def expand_task(request):
    task_id = request.GET['task_id']
    task = get_object_or_404(Task, task_id=task_id)
    context = {
        'order': task.ref_order,
        'task': task,
        'actions': ExecutionPlan.get_actions_by_task(task)
    }

    return render(request, 'orders/control_action_tab.html', context)


def preview_close_task(request, task_id):
    task = get_object_or_404(Task, task_id=task_id)
    context = {
        'order': task.ref_order,
        'task': task,
        'actions': ExecutionPlan.get_actions_by_task(task)
    }

    return render(request, 'orders/close_action_tab.html', context)


def expand_action(request):
    action_id = request.GET['action_id']
    action = get_object_or_404(ExecutionPlan, id=action_id)
    context = {
        'order': action.ref_task.ref_order,
        'task': action.ref_task,
        'action': action,
        'cards': Card.get_cards_by_action(action)
    }

    return render(request, 'orders/control_card_tab.html', context)


def start_action(request):
    action_id = request.GET['action_id']
    action = get_object_or_404(ExecutionPlan, id=action_id)
    action.start_date = datetime.date.today()
    action.save()
    if action.plan_type == 0:
        import_cards = Card.get_leader_cards(action)
        for card in import_cards:
            title = get_title_from_parent(card, action.target)
            new_card = Card(ref_action=action,
                            start_date=datetime.date.today(),
                            object_id=card.object_id,
                            object_full_name=card.object_full_name,
                            doc_qty=card.doc_qty,
                            doc_title=title,
                            doc_type=action.target)
            new_card.save()
    context = {
        'order': action.ref_task.ref_order,
        'task': action.ref_task,
        'action': action,
        'actions': ExecutionPlan.get_actions_by_task(action.ref_task),
        'cards': Card.get_cards_by_action(action)
    }

    return render(request, 'orders/control_action_tab.html', context)


def expand_card(request):
    card_id = request.GET['card_id']
    card = get_object_or_404(Card, execution_id=card_id)

    context = {
        'action': card.ref_action,
        'task': card.ref_action.ref_task,
        'order': card.ref_action.ref_task.ref_order
    }

    return render(request, 'orders/parent_card.html', context)


def card_create(request, ref_action):
    action = get_object_or_404(ExecutionPlan, id=ref_action)
    context = {}
    if request.method == 'POST':
        if request.POST.get('execution_id', None):
            card = get_object_or_404(Card, execution_id=request.POST['execution_id'])
            form = ExecutionCardForm(request.POST, request.FILES, instance=card)
        else:
            form = ExecutionCardForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save()
            post.refresh_from_db()
            form = ExecutionCardForm(instance=post)
            context['success'] = 'Объект был успешно создан/обновлен!'
    else:
        form = ExecutionCardForm(initial={
            'ref_action': action.id,
            'doc_qty': 1,
            'doc_type': action.target
        })
    context['form'] = form
    return render(request, 'orders/card_create.html', context)


def card_detail(request, execution_id):
    card = get_object_or_404(Card, execution_id=execution_id)
    context = {'execution': card,
               'action_id': card.ref_action.id}
    if request.method == 'POST':
        form = ExecutionCardForm(request.POST, request.FILES, instance=card)
        if form.is_valid():
            post = form.save()
            context['form'] = form
            context['execution'] = post
            context['success'] = 'Документ был успешно отредактирован!'
        else:
            context['form'] = form
    else:
        context['form'] = ExecutionCardForm(instance=card)

    return render(request, 'orders/card_detail.html', context)


def generate_request(request, action_id, doc_type):
    action = get_object_or_404(ExecutionPlan, id=action_id)
    if doc_type == 'sez':
        return generate_sez_request(action)
    if doc_type == 'letter':
        return generate_letter_request(action)
    else:
        return None


def create_extended_order(request, master_id):
    master_order = get_object_or_404(Order, order_id=master_id)
    new_order = Order(order_id=get_new_value('order_ext'),
                      master_id=master_id,
                      client=master_order.client,
                      client_id=master_order.client_id,
                      description='Расширение к заявке: '+master_id,
                      region=master_order.region)
    new_order.save()
    order_form = OrderForm(instance=new_order)
    context = {
        'order': new_order,
        'form': order_form,
    }
    return render(request, 'orders/order_detail.html', context)


def ajax_client_contract(request):
    client = get_object_or_404(Client, id=request.GET.get('client_id', None))
    contracts = client.get_available_contracts()
    service_order = get_object_or_404(Order, order_id='service')
    context = {
        'client': client,
        'contracts': contracts,
        'order_contracts': service_order.contracts.all(),
    }

    return render(request, 'orders/include/order_contracts.html', context)


def ajax_expand_contract(request):
    contract = get_object_or_404(Contract, id=request.GET.get('contract_id', None))
    order_id = request.GET.get('order_id', None)
    if order_id:
        service_order = get_object_or_404(Order, order_id=order_id)
    else:
        service_order = get_object_or_404(Order, order_id='service')
    context = {
        'contract': contract,
        'sub_contracts': contract.get_child(),
        'order': service_order,
    }

    return render(request, 'orders/include/sub_contracts.html', context)


def ajax_add_contract(request):
    contract = get_object_or_404(Contract, id=request.GET.get('contract_id', None))
    order_id = request.GET.get('order_id', None)
    if order_id:
        service_order = get_object_or_404(Order, order_id=order_id)
    else:
        service_order = get_object_or_404(Order, order_id='service')
    service_order.contracts.add(contract)
    context = {
        'order_contracts': service_order.contracts.all()
    }
    return render(request, 'orders/include/contracts_belong_order.html', context)


def ajax_remove_contract(request):
    contract = get_object_or_404(Contract, id=request.GET.get('contract_id', None))
    order_id = request.GET.get('order_id', None)
    if order_id:
        service_order = get_object_or_404(Order, order_id=order_id)
    else:
        service_order = get_object_or_404(Order, order_id='service')
    service_order.contracts.remove(contract)
    context = {
        'order_contracts': service_order.contracts.all()
    }
    return render(request, 'orders/include/contracts_belong_order.html', context)
