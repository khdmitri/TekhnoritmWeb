from django.shortcuts import render, get_object_or_404
from .forms import MessageForm, AnswerForm
from .models import Message, Alert
from accounts.models import Profile
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

# Create your views here.


def show_messages(request, box, type, message):
    context = {}
    context['message'] = message
    if box == 'inbox':
        profile = Profile.objects.filter(user=request.user).first()
        objects = Message.get_inbox(profile=profile)
        context = {
            'box': 'ВХОДЯЩИЕ',
            'parent_box': 'inbox',
            'department': objects['department'],
            'personal': objects['personal'],
        }
        return render(request, 'int_messages/message_list_inbox.html', context)
    elif box == 'outbox':
        context['box'] = 'ИСХОДЯЩИЕ'
        context['parent_box'] = 'outbox'
        context['object_list'] = Message.get_outbox(sender=request.user)

    return render(request, 'int_messages/message_list_outbox.html', context)


@login_required()
def create_message(request):
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save()
            post.refresh_from_db()
            post.ticket_id = post.id
            post.save()
            return HttpResponseRedirect(reverse('int_messages:message-list', kwargs={
                'box': 'outbox',
                'type': 'all',
                'message': 'success',
            }))
    else:
        data = {'sender': request.user}
        form = MessageForm(initial=data)
    context = {
        'form': form,
    }
    return render(request, 'int_messages/message_create.html', context)


@login_required()
def detail_message(request, message_id, parent_box):
    print('MESSAGE_DETAIL!!!!')
    message = get_object_or_404(Message, id=message_id)
    message.unread = False
    message.save()
    history = Message.get_messages_by_ticket(message.ticket_id, message_id)
    initial_data = {
        'sender': request.user,
        'ticket_id': message.ticket_id,
        'receiver_staff': message.sender,
        'topic': 'Re:'+message.topic,
    }
    form = AnswerForm(initial=initial_data)
    context = {
        'parent_box': parent_box,
        'message': message,
        'history': history,
        'form': form,
    }

    return render(request, 'int_messages/message_detail.html', context)


@login_required()
def detail_alert(request, alert_id):
    alert = get_object_or_404(Alert, id=alert_id)
    alert.unread = False
    alert.save()
    context = {
        'alert': alert,
    }

    return render(request, 'int_messages/alert_detail.html', context)


def answer_message(request):
    if request.method == 'POST':
        form = AnswerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('int_messages:message-list', kwargs={
                'box': 'outbox',
                'type': 'all',
                'message': 'success',
            }))
    return render(request, 'int_messages/message_detail.html')


def close_topic(request, ticket_id, parent_box):
    qs = Message.get_messages_by_ticket(ticket_id, None)
    for message in qs:
        message.closed = True
        message.save()
    return HttpResponseRedirect(reverse('int_messages:message-list', kwargs={
        'box': parent_box,
        'type': 'all',
        'message': 'success',
    }))
