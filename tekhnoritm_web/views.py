from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from int_messages.models import Message, Alert
from django.http import JsonResponse


def start_app(request):
    # if auth.get_user(request).is_authenticated:
    #     return redirect('workflow:home')
    # else:
    if request.user.is_authenticated:
        return redirect('workflow:home')
    else:
        return redirect('accounts:custom-login')


def ajax_mark_as_red(request):
    obj_type = request.GET['obj_type']
    obj_id = request.GET['obj_id']
    if obj_type == 'alert':
        alert = Alert.objects.get(id=obj_id)
        if alert:
            alert.unread = False
            alert.save()
    else:
        message = Message.objects.get(id=obj_id)
        if message:
            message.unread = False
            message.save()
    data = {
        'success': True
    }
    return JsonResponse(data)


def ajax_alarms(request):
    context = {}
    if request.user.is_authenticated:
        limit = 10
        new_messages = Message.get_new_messages(request.user.profile, limit)
        if new_messages:
            message_val = len(new_messages['department'])+len(new_messages['personal'])
            if message_val >= limit:
                message_val = str(limit)+'+'
            elif message_val == 0:
                message_val = ''
            else:
                message_val = str(message_val)
        else:
            message_val = ''

        new_alerts = Alert.get_new_alerts(request.user.profile, limit)
        if new_alerts:
            alert_val = len(new_alerts['department'])+len(new_alerts['personal'])
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
    return render(request, 'ajax_items.html', context)
