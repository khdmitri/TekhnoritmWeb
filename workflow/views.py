from django.shortcuts import render, get_object_or_404, reverse
from int_messages.models import Message, Alert
from laboratory.cron import check_pribor_expire_date
from django.http import HttpResponseRedirect

# Create your views here.


def init_workflow(request):
    context = {}
    if request.user.is_authenticated:
        dep = request.user.profile.department
        if dep and dep.name == 'Испытательная лаборатория':
            check_pribor_expire_date(14)

        limit = 10
        new_messages = Message.get_new_messages(request.user.profile, limit)
        if new_messages:
            message_val = len(new_messages['department']) + len(new_messages['personal'])
            if message_val >= limit:
                message_val = str(limit) + '+'
            elif message_val == 0:
                message_val = ''
            else:
                message_val = str(message_val)
        else:
            message_val = ''

        new_alerts = Alert.get_new_alerts(request.user.profile, limit)
        if new_alerts:
            alert_val = len(new_alerts['department']) + len(new_alerts['personal'])
            if alert_val >= limit:
                alert_val = str(limit) + '+'
            elif alert_val == 0:
                alert_val = ''
            else:
                alert_val = str(alert_val)
        else:
            alert_val = ''

        context = {
            'new_messages': new_messages,
            'new_alerts': new_alerts,
            'alerts_val': alert_val,
            'messages_val': message_val,
        }
        context['title'] = 'ЭД: Рабочее пространство'
    return render(request, 'workflow/home.html', context)


def cleric_view(request):
    return render(request, 'workflow/cleric_view.html')


def inspection_view(request):
    return render(request, 'workflow/cleric_view.html')


def laboratory_view(request):
    return render(request, 'workflow/cleric_view.html')


def hide_message(request, msg_type, msg_id):
    obj = None
    if msg_type == 'alert':
        obj = get_object_or_404(Alert, id=msg_id)
    elif msg_type == 'message':
        obj = get_object_or_404(Message, id=msg_id)
    if obj is not None:
        obj.unread = False
        obj.save()

    return HttpResponseRedirect(reverse('workflow:home'))
