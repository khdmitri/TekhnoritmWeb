# -*- coding: utf-8 -*-

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from accounts.models import Profile, Department
from accounts.forms import ProfileForm
from references.models import UniBook

# Create your views here.


@permission_required('site_administrator')
def staff_view(request, title=None):
    users = User.objects.all()
    context = {
        'users': users,
    }
    if title is not None:
        context['title'] = title
    return render(request, 'site_admin/staff_view.html', context)


def staff_detail(request, username):
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.filter(user=user).first()
    profile_form = ProfileForm(instance=profile)
    context = {
        'selected_user': user,
        'form': profile_form,
    }

    return render(request, 'site_admin/staff_detail.html', context)


@permission_required('site_administrator')
def staff_save(request):
    context = {}
    if request.method == 'POST':
        user = User.objects.filter(id=request.POST['user']).first()
        profile_form = ProfileForm(request.POST, request.FILES, instance=Profile.objects.filter(user=user)[0])
        context = {
            'selected_user': user,
            'form': profile_form,
        }

        if profile_form.is_valid():
            perm = None
            if profile_form.cleaned_data['department']:
                dep = profile_form.cleaned_data['department']
                perm = dep.default_perm
            post = profile_form.save()
            post.position = profile_form.cleaned_data['position']
            post.department = profile_form.cleaned_data['department']
            post.avatar = profile_form.cleaned_data['avatar']
            post.save()
            if perm:
                user.user_permissions.add(perm)
            context = {
                'title': UniBook.get_objects_by_category('staff_success_edit').first().item,
            }
            return HttpResponseRedirect(reverse('site_admin:staff-view-context', kwargs=context))
    return render(request, 'site_admin/staff_detail.html', context)
