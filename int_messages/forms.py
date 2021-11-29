from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sender', 'receiver_staff', 'receiver_department', 'unread', 'topic', 'body', 'ticket_id', 'attach']
        widgets = {
            'sender': forms.HiddenInput(),
            'unread': forms.HiddenInput(),
            'ticket_id': forms.HiddenInput(),
            'body': forms.Textarea(),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sender', 'receiver_staff', 'topic', 'body', 'ticket_id', 'attach']
        widgets = {
            'sender': forms.HiddenInput(),
            'ticket_id': forms.HiddenInput(),
            'receiver_staff': forms.HiddenInput(),
            'body': forms.Textarea(),
        }
