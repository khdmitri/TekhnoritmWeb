from .models import Alert


def new_alert(context):
    '''context = {
                    alert_code: 100 - Order created, details required
                    action_url: alert action url
                    position: receiver position
                    department: receiver department
                    topic
                    body
                }'''
    new_alert = Alert()
    try:
        new_alert.code = context['alert_code']
        new_alert.action_url = context['action_url']
        new_alert.receiver_position = context['position']
        new_alert.receiver_department = context['department']
        new_alert.topic = context['topic']
        new_alert.body = context['body']
        if 'alert_code_2' in context:
            new_alert.alert_code = context['alert_code_2']
        new_alert.save()
    except Exception as e:
        return {'success': False, 'error': e}

    return {'success': True}


def mark_alert_as_red(alert_code, department):
    alerts = Alert.objects.filter(code=alert_code).filter(receiver_department=department).filter(unread=True)
    for alert in alerts:
        alert.unread = False
        alert.save()
