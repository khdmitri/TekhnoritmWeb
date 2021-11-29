from tekhnoritm_web.celery import app
from .models import ControlConfig, AlertPersonality
from orders.models import ExecutionPlan
from int_messages.models import Alert
from int_messages.service import new_alert
from accounts.models import Department
from datetime import date, timedelta


def send_alert(task, alert_code, department=None, profile=None):
    topic = ''
    if alert_code.startswith('D_'):
        topic = 'Предупреждение уровня КРАСНЫЙ: '
    elif alert_code.startswith('W_'):
        topic = 'Предупреждение уровня :ЖЕЛТЫЙ: '
    topic += 'Нарушение сроков выполнения работы по заявкам: '+task.ref_task.task_id+'->'+task.ref_task.ref_order.order_id
    body = 'Клиент: '+task.ref_task.ref_order.client.short_name+'\n'
    description = task.ref_task.ref_order.description if task.ref_task.ref_order.description else 'Нет описания'
    body += 'Заявка: '+task.ref_task.ref_order.order_id+'-> '+description+'\n'
    description = task.description if task.description else 'Нет описания'
    body += 'Внутреняя заявка: '+task.ref_task.task_id+'-> '+description+'\n'
    body += 'Цель: '+task.target+'-> '+task.get_target_description()+'\n'
    body += 'Прогресс: '+str(task.get_progress()) + '\n'
    delta = date.today() - task.start_date
    body += 'Сроки: НАЧАЛО->'+task.start_date.strftime('%d.%m.%Y')+' - ОКОНЧАНИЕ отсутствует в течение '+str(delta.days)+' дней'
    alert_context = {
        'alert_code': -task.id,
        'alert_code_2': alert_code,
        'action_url': task.get_absolute_url(),
        'position': profile,
        'department': department,
        'topic': topic,
        'body': body,
    }
    status = new_alert(alert_context)
    print('Celery task execution status:', status)


@app.task
def spam_test():
    print('Spam test passed!')


@app.task
def send_alerts_by_dates():
    # Сначала выберем оповещение с планом DANGER
    ccs = ControlConfig.objects.filter(is_dang_alert=True)
    for cc in ccs:
        # Для каждого оповещения найдем задачи
        tasks = ExecutionPlan.objects.filter(start_date__isnull=False).filter(stop_date__isnull=True).filter(
            target=cc.ref_task.target).filter(
            ref_task__task_type=cc.ref_task.task_type)

        for task in tasks:
            # Если наступает danger_date
            if date.today() >= task.start_date + timedelta(days=cc.dang_days):
                alert_code = 'D_EP-'+str(task.id)
                if cc.dang_alert_type == 1:
                    if not Alert.get_alerts_by_alert_code(alert_code):
                        def_department = Department.objects.get(name='АХО (Администрация)')
                        send_alert(task=task, alert_code=alert_code, department=def_department)
                        receivers = AlertPersonality.get_alerts_by_task(task=cc)
                        for receiver in receivers:
                            send_alert(task=task, alert_code=alert_code, profile=receiver.ref_profile)
                elif cc.dang_alert_type == 2:
                    def_department = Department.objects.get(name='АХО (Администрация)')
                    send_alert(task=task, alert_code=alert_code, department=def_department)
                    receivers = AlertPersonality.get_alerts_by_task(task=cc)
                    for receiver in receivers:
                        send_alert(task=task, alert_code=alert_code, profile=receiver)
            # Если наступает warn_date
            elif date.today() >= task.start_date + timedelta(days=cc.warn_days) and cc.is_warn_alert:
                alert_code = 'W_EP-' + str(task.id)
                if cc.warn_alert_type == 1:
                    if not Alert.get_alerts_by_alert_code(alert_code):
                        def_department = Department.objects.get(name='АХО (Администрация)')
                        send_alert(task=task, alert_code=alert_code, department=def_department)
                        receivers = AlertPersonality.get_alerts_by_task(task=cc)
                        for receiver in receivers:
                            send_alert(task=task, alert_code=alert_code, profile=receiver.ref_profile)
                elif cc.warn_alert_type == 2:
                    def_department = Department.objects.get(name='АХО (Администрация)')
                    send_alert(task=task, alert_code=alert_code, department=def_department)
                    receivers = AlertPersonality.get_alerts_by_task(task=cc)
                    for receiver in receivers:
                        send_alert(task=task, alert_code=alert_code, profile=receiver)

