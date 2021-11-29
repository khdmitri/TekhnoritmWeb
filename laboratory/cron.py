from .models import Pribor
from django.urls import reverse
from accounts.models import Department
from int_messages.service import new_alert
from int_messages.models import Alert
from datetime import datetime
import datetime as DT


def check_pribor_expire_date(delta=7, check_days=1):
    print('cron: check expire dates - START!')
    check_date = datetime.now() - DT.timedelta(days=check_days)
    warn_list = Pribor.get_expired()
    if warn_list:
        body = ''
        for pribor in warn_list:
            if len(body) > 0:
                body += ', '
            body += pribor.name
        alert_context = {
            'alert_code': 310,
            'action_url': reverse('laboratory:pribor-warn-list'),
            'position': None,
            'department': Department.objects.get(name='Испытательная лаборатория'),
            'topic': 'Имеется оборудование, с истекающими сроками поверки',
            'body': 'Просим обратить внимание на оборудование, требующее обновление поверки: '+body
        }
        if not Alert.get_alert_by_code_body_date(check_date, 310, alert_context['body']):
            new_alert(alert_context)
    print('cron: check expire dates - END!')
