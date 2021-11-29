from django.shortcuts import render, get_object_or_404

from int_messages.service import new_alert
from .models import Client, DefaultTasks, UniBook2, RequestPerson, Region, Contract
from .forms import ClientForm, DefaultTaskForm, UniBook2Form, RequestPersonForm, ContractForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import permission_required

# Create your views here.
TASK_ITEMS = {
    "Работы по схеме Р1": 'R1',
    "Работы по схеме Р2": 'R2',
    "Производственный контроль (ПРТО)": 'PK-PRTO',
    "Производственный контроль (лаборатория)": 'PK',
    "СОУТ": 'SOUT',
    "Иное": 'OTHER',
}


def client_list(request, success=None):
    if success:
        context = {'success': success}
    else:
        context = {}
    clients = Client.objects.all()[:20]
    context['clients'] = clients

    return render(request, 'references/client_list.html', context)


def client_create(request):
    if request.method == 'POST':
        form = ClientForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            context = {
                'success': 'Карточка клиента была успешно добавлена!',
            }
            return HttpResponseRedirect(reverse('references:client-list-success', kwargs=context))
    else:
        form = ClientForm()
    return render(request, 'references/client_create.html', {'form': form})


def client_delete(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.delete()
    return HttpResponseRedirect(reverse('references:client-list'))


def contract_delete(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    orders = contract.order_set.all()
    is_ready = True
    if orders:
        is_ready = False
        message = {
            'alert_class': 'alert-warning',
            'text': 'Нельзя удалить договор, так как имеются заявки, привязанные к данному договору!'
        }
    if is_ready:
        contract.delete()
        message = {
            'alert_class': 'alert-info',
            'text': 'Договор был успешно удален!'
        }
    return HttpResponseRedirect(reverse('references:client-contracts-message', args=(contract.ref_client.id,
                                                                                     message['alert_class'],
                                                                                     message['text'],)))


def ajax_search_list(request):
    search_line = request.GET['search_line']
    if search_line:
        clients = Client.objects.filter(Q(short_name__icontains=search_line) | Q(long_name__icontains=search_line))[:20]
    else:
        clients = Client.objects.all()[:20]
    context = {
        'clients': clients,
    }
    return render(request, 'references/client_list_ajax.html', context)


def ajax_client_list(request):
    search_line = request.GET['search_line']
    if search_line:
        clients = Client.objects.filter(Q(short_name__icontains=search_line) | Q(long_name__icontains=search_line))[:20]
    else:
        clients = Client.objects.all()[:20]
    context = {
        'clients': clients,
    }
    return render(request, 'references/client_list_ajax_v2.html', context)


def get_available_contracts(request):
    client = get_object_or_404(Client, id=request.GET['client_id'])
    available_contracts = client.get_available_contracts()
    context = {
        'contracts': available_contracts
    }

    return render(request, 'references/include/available_contracts.html', context)


def create_contract(request, client_id=None, contract_id=None):
    context = {}
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES)
        client = get_object_or_404(Client, id=request.POST['client_id'])
        if form.is_valid():
            pre_form = form.save(commit=False)
            pre_form.ref_client = client
            if form.cleaned_data['is_parent']:
                parent = None
                pre_form.ref_parent = parent
            pre_form.save()
            pre_form.refresh_from_db()
            context = {
                'client': client,
                'messages': [
                    {
                        'alert_class': 'alert-success',
                        'text': 'Контракт успешно добавлен!'
                    }
                ]
            }
            contract_obj = get_object_or_404(Contract, id=pre_form.pk)
            alert_context = {
                'alert_code': 109,
                'action_url': contract_obj.get_absolute_url(),
                'position': None,
                'department': request.user.profile.department,
                'topic': 'Создан контракт №'+str(contract_obj.id),
                'body':  'Контракт после его создания ожидает привязки к заявке',
            }
            status = new_alert(alert_context)
            print('Alert status:', status)
            return HttpResponseRedirect(reverse('references:client-contracts', kwargs={'client_id': client.id}))
    else:
        contracts = None
        if client_id:
            client = get_object_or_404(Client, id=client_id)
            parent = None
            contracts = client.get_available_contracts()
            if contract_id and contract_id > 0:
                parent = get_object_or_404(Contract, id=contract_id)
                is_parent = False
            else:
                is_parent = True
            form = ContractForm(initial={
                'is_parent': is_parent,
                'client_id': client.id,
                'client_name': client.short_name,
                'ref_client': client,
                'ref_parent': parent,
            })
        else:
            form = ContractForm()
        context['contracts'] = contracts
    context['form'] = form
    return render(request, 'references/contract_create.html', context)


def contract_detail(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    if request.method == 'POST':
        form = ContractForm(request.POST, request.FILES, instance=contract)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('references:client-contracts', kwargs={'client_id': contract.ref_client.id}))
    else:
        form = ContractForm(instance=contract)
    context = {
        'form': form,
        'contract': contract,
        'client': contract.ref_client
    }
    return render(request, 'references/contract_detail.html', context)


def default_task_list(request):
    selected_item = request.GET['selected_item']
    tasks = DefaultTasks.objects.filter(task_type=TASK_ITEMS[selected_item]).order_by('position')
    context = {
        'selected_item': selected_item,
        'tasks': tasks,
    }

    return render(request, 'references/default_task_list_ajax.html', context)


def default_task(request):
    context = {
        'task_items': TASK_ITEMS.keys()
    }
    return render(request, 'references/default_tasks.html', context)


def default_task_create(request, task_type):
    task_type_code = TASK_ITEMS[task_type]
    context = {}
    if request.method == 'POST':
        form = DefaultTaskForm(request.POST)
        form.task_type = task_type_code
        if form.is_valid():
            post = form.save()
            post.refresh_from_db()
            context = {
                'task_id': post.pk
            }
            return HttpResponseRedirect(reverse('references:default-task-detail', kwargs=context))
        else:
            context = {
                'form': form,
                'task_type': task_type_code,
            }
    else:
        form = DefaultTaskForm(initial={'task_type': task_type_code})
        context = {
            'form': form,
            'task_type': task_type_code,
        }
    return render(request, 'references/default_task_create.html', context)


def default_task_detail(request, task_id):
    context = None
    task_obj = get_object_or_404(DefaultTasks, id=task_id)
    if request.method == 'POST':
        form = DefaultTaskForm(request.POST, instance=task_obj)
        form.id = task_id
        if form.is_valid():
            form.save()
            context = {
                'task_id': task_id,
                'form': form,
                'success': 'Запись набора была успешно отредактирована!'
            }
    else:
        form = DefaultTaskForm(instance=task_obj)
        context = {
            'task_id': task_id,
            'form': form,
        }
    return render(request, 'references/default_task_detail.html', context)


def client_detail(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client_form = ClientForm(instance=client)
    context = {
        'client': client,
        'form': client_form,
    }
    return render(request, 'references/client_detail.html', context)


def client_contract(request, client_id, alert_class=None, text=None):
    client = get_object_or_404(Client, id=client_id)
    contracts = client.get_parent_contracts()
    messages = None
    if text:
        messages = [
            {
                'alert_class': alert_class,
                'text': text,
            }
        ]
    context = {
        'client': client,
        'contracts': contracts,
        'messages': messages,
    }
    return render(request, 'references/contract_list.html', context)


def contract_close(request, contract_id):
    contract = get_object_or_404(Contract, id=contract_id)
    orders = contract.order_set.all()
    is_ready = True
    for order in orders:
        if not order.close_date:
            is_ready = False
            message = {
                'alert_class': 'alert-warning',
                'text': 'Нельзя закрыть договор, так как имеются незавершенные заявки для данного договора!'
            }
    if is_ready:
        message = {
            'alert_class': 'alert-info',
            'text': 'Договор был успешно закрыт!'
        }
    return HttpResponseRedirect(reverse('references:client-contracts-message', args=(contract.ref_client.id,
                                                                                     message['alert_class'],
                                                                                     message['text'],)))


def expand_contract(request):
    contract = get_object_or_404(Contract, id=request.GET['contract_id'])
    sub_contracts = contract.get_child()
    context = {
        'client': contract.ref_client,
        'contract': contract,
        'sub_contracts': sub_contracts,
    }
    if not sub_contracts:
        context['messages'] = [
            {
                'alert_class': 'alert-warning',
                'text': 'Дополнительные соглашения не найдены!'
            }]
    return render(request, 'references/expanded_contract.html', context)


def client_save(request):
    context = {}
    if request.method == 'POST':
        client_form = ClientForm(request.POST, request.FILES, instance=Client.objects.get(pk=request.POST['pk']))
        if client_form.is_valid():
            client_form.save()
            context = {
                'success': 'Карта клиента была успешно отредактирована!',
            }
            return HttpResponseRedirect(reverse('references:client-list-success', kwargs=context))
    return render(request, 'references/client_detail.html', context)


def default_task_delete(request, task_id):
    obj = get_object_or_404(DefaultTasks, id=task_id)
    obj.delete()

    return render(request, 'references/default_task_deleted.html')


@permission_required('site_administrator')
def show_ref_category(request):
    context = {
        'categories': UniBook2.get_categories(),
        'form': UniBook2Form()
    }

    return render(request, 'references/ref_category.html', context)


def load_category(request):
    cat_type = request.GET['cat_type']
    context = {
        'cat_items': UniBook2.get_objects_by_category(cat_type),
        'form': UniBook2Form(initial={'category': cat_type})

    }

    return render(request, 'references/category_form.html', context)


def category_post(request):
    context = {}
    if request.method == 'POST':
        if request.POST.get('id', None):
            # Record exist
            model_obj = get_object_or_404(UniBook2, id=request.POST['id'])
            form = UniBook2Form(request.POST, instance=model_obj)
            if form.is_valid():
                form.save()
                form = UniBook2Form(instance=model_obj)
                context['success'] = 'Запись успешно отредактирована!'
            context['form'] = form
        else:
            # New record
            form = UniBook2Form(request.POST)
            if form.is_valid():
                post = form.save()
                post.refresh_from_db()
                model_obj = get_object_or_404(UniBook2, id=post.pk)
                form = UniBook2Form(instance=model_obj)
                context['success'] = 'Запись успешно создана!'
            context['form'] = form
        if request.POST.get('category', None):
            context['cat_items'] = UniBook2.get_objects_by_category(request.POST['category'])
    return render(request, 'references/category_form.html', context)


def delete_category_item(request):
    item_id = request.GET['item_id']
    model_obj = get_object_or_404(UniBook2, id=item_id)
    cat_type = model_obj.category
    model_obj.delete()

    context = {
        'cat_items': UniBook2.get_objects_by_category(cat_type),
        'form': UniBook2Form(initial={'category': cat_type})
    }

    return render(request, 'references/category_form.html', context)


def load_request_person(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    context = {
        'regions': Region.objects.all(),
        'client': client,
        'requests': RequestPerson.get_requests_by_client(client)
    }

    return render(request, 'references/request_person.html', context)


def prepare_request_person(request):
    client = get_object_or_404(Client, id=request.GET['client_id'])
    selected_region = None
    if request.GET.get('request_id', None):
        rp = get_object_or_404(RequestPerson, id=request.GET['request_id'])
        selected_region = rp.ref_region
        form = RequestPersonForm(instance=rp)
    else:
        form = RequestPersonForm(initial={
            'ref_client': client
        })
    context = {
        'client': client,
        'form': form,
        'regions': Region.objects.all(),
        'selected_region': selected_region
    }

    return render(request, 'references/request_person_form.html', context)


def request_person_post(request):
    success = None
    context = None
    selected_region = None
    if request.method == 'POST':
        if request.POST['id']:
            # Edit
            rp = get_object_or_404(RequestPerson, id=request.POST['id'])
            form = RequestPersonForm(request.POST, instance=rp)
            if form.is_valid():
                post = form.save()
                form = RequestPersonForm(instance=post)
                selected_region = post.ref_region
                success = 'Успешно отредактировано!'
        else:
            # Create
            form = RequestPersonForm(request.POST)
            if form.is_valid():
                post = form.save()
                selected_region = post.ref_region
                form = RequestPersonForm(instance=post)
                success = 'Успешно создано!'

        client = get_object_or_404(Client, id=request.POST['ref_client'])
        context = {
            'selected_region': selected_region,
            'client': client,
            'form': form,
            'requests': RequestPerson.get_requests_by_client(client),
            'success': success,
            'regions': Region.objects.all(),
        }

    return render(request, 'references/request_person_table.html', context)


def delete_request_person(request):
    rp = get_object_or_404(RequestPerson, id=request.GET['record_id'])
    rp.delete()
    client = get_object_or_404(Client, id=request.GET['client_id'])
    context = {
        'client': client,
        'requests': RequestPerson.get_requests_by_client(client)
    }

    return render(request, 'references/request_person_table.html', context)
