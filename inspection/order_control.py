from orders.models import Task, ExecutionPlan, Card, Order
from inspection.models import CommonObjectInfo, ResultDocument
import datetime


OBJ_TARGETS = {
    'see': {
        'task_type': 'R1',
        'task_type_alt': '',
        'target': 'SEE'
    },
    'oos': {
            'task_type': 'R1',
            'task_type_alt': '',
            'target': 'OOS'
    },
    'protocol': {
            'task_type': 'R2',
            'task_type_alt': 'PK-PRTO',
            'target': 'PROTOCOL'
    },
    'ez': {
            'task_type': 'R2',
            'task_type_alt': 'PK-PRTO',
            'target': 'EZ-R2'
    },
}


def link_to_order(obj_type, obj):
    order = obj.ref_object.ref_order
    task = Task.objects.filter(ref_order=order).filter(task_type=OBJ_TARGETS[obj_type]['task_type'])
    if not task:
        task = Task.objects.filter(ref_order=order).filter(task_type=OBJ_TARGETS[obj_type]['task_type_alt'])
        if not task:
            slave_orders = Order.get_slaves(order)
            if slave_orders:
                for slave in slave_orders:
                    task = Task.objects.filter(ref_order=slave).filter(task_type=OBJ_TARGETS[obj_type]['task_type'])
                    if not task:
                        task = Task.objects.filter(ref_order=slave).filter(
                            task_type=OBJ_TARGETS[obj_type]['task_type_alt'])
                    if task:
                        break
    if task:
        task = task[0]
        action = ExecutionPlan.objects.filter(ref_task=task).filter(target=OBJ_TARGETS[obj_type]['target'])
        if action:
            action = action[0]
            # clean existing cards if exist
            old_cards = Card.objects.filter(ref_action=action).filter(doc_type=OBJ_TARGETS[obj_type]['target'])
            for old_card in old_cards:
                if old_card.object_id == obj.ref_object.id:
                    old_card.delete()
            new_card = Card.objects.create(ref_action=action, doc_type=OBJ_TARGETS[obj_type]['target'],
                                           doc_title=obj.ref_object.name)
            if obj_type == 'see':
                if isinstance(obj, ResultDocument):
                    new_card.doc_no = '---'
                    new_card.doc_base = obj.document_type
                    new_card.object_id = obj.ref_object.id
                else:
                    new_card.doc_no = obj.see_no
                    new_card.doc_date = obj.see_date
                    new_card.doc_base = obj.project_header
                    new_card.object_id = obj.ref_object.id

                    prto_name = obj.ref_object.prto_type_ref.name_visible + ' ' + obj.ref_object.name
                    sharing = ''
                    if obj.ref_object.is_shared:
                        sharing = ' совместно с (sharing) ' + obj.ref_object.shared_name + \
                                  ' по стандартам ' + obj.ref_object.shared_standard + ' ' + obj.ref_object.shared_owner
                    common_info = CommonObjectInfo.objects.filter(ref_order=obj.ref_object.ref_order).first()
                    full_prto_name = prto_name + ' ' + obj.standard + ' принадлежащий ' + common_info.ref_owner.short_name + sharing
                    new_card.object_full_name = full_prto_name

            elif obj_type == 'protocol':
                if isinstance(obj, ResultDocument):
                    new_card.doc_no = '---'
                    new_card.doc_base = obj.document_type
                    new_card.object_id = obj.ref_object.id
                else:
                    see_card = Card.get_card_by_object_target(obj.ref_object.id, 'SEE')
                    new_card.doc_no = obj.protocol_no
                    new_card.doc_date = obj.protocol_date
                    new_card.object_id = obj.ref_object.id
                    if see_card:
                        new_card.object_full_name = see_card.object_full_name
            elif obj_type == 'ez':
                if isinstance(obj, ResultDocument):
                    new_card.doc_no = '---'
                    new_card.doc_base = obj.document_type
                    new_card.object_id = obj.ref_object.id
                else:
                    see_card = Card.get_card_by_object_target(obj.ref_object.id, 'SEE')
                    new_card.doc_no = obj.ez_no
                    new_card.doc_date = obj.ez_date
                    new_card.object_id = obj.ref_object.id
                    if see_card:
                        new_card.object_full_name = see_card.object_full_name
            elif obj_type == 'oos':
                see_card = Card.get_card_by_object_target(obj.ref_object.id, 'SEE')
                new_card.doc_no = '---'
                new_card.doc_date = datetime.date.today()
                new_card.object_id = obj.ref_object.id
                if see_card:
                    new_card.object_full_name = see_card.object_full_name

            new_card.save()
            return {'success': True,
                    'obj': new_card,
                    'msg': 'Карта объекта успешно присоединена к заявке: '+new_card.ref_action.ref_task.ref_order.order_id+'!'}
        return {'success': False,
                'obj': None,
                'msg': 'Внутри заявки данный вид работ не найден! (Обратитесь к разработчику)'}
    return {'success': False,
            'obj': None,
            'msg': 'Внутреняя заявка на данный вид работ не найдена!'}
