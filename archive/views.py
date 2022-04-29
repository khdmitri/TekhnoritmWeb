from django.shortcuts import render
from django.db.models import Q
from .forms import ArchiveForm
from .models import ArchiveObject
from orders.models import Card

# Create your views here.


def archive_view(request):
    if request.method == 'POST':
        form = ArchiveForm(request.POST)
        search_result = None
        context = {'form': form}
        if form.is_valid():
            search_result = ArchiveObject.objects.all()
            if form.cleaned_data.get('from_date', False):
                search_result.filter(create_date__gte=form.cleaned_data['from_date'])
            if form.cleaned_data.get('to_date', False):
                search_result.filter(create_date__lte=form.cleaned_data['to_date'])
            if form.cleaned_data.get('order_context', False):
                search_result.filter(Q(ref_order__order_id__icontains=form.cleaned_data['order_context']) |
                                     Q(ref_order__ext_order_id__icontains=form.cleaned_data['order_context']) |
                                     Q(ref_order__client__short_name__icontains=form.cleaned_data['order_context']) |
                                     Q(ref_order__client__long_name__icontains=form.cleaned_data['order_context']) |
                                     Q(ref_order__region__contains=form.cleaned_data['order_context']))
            if form.cleaned_data.get('task_context', False):
                search_result.filter(Q(ref_task__task_id__contains=form.cleaned_data['task_context']) |
                                     Q(ref_task__distribution_dep__description__icontains=form.cleaned_data['task_context']) |
                                     Q(ref_task__distribution_dep__name__contains=form.cleaned_data['task_context']) |
                                     Q(ref_task__task_type__contains=form.cleaned_data['task_context']))
            if form.cleaned_data.get('execution_context', False):
                search_result.filter(Q(ref_execution__int_executor__description__icontains=form.cleaned_data['execution_context']) |
                                     Q(ref_execution__int_executor__name__icontains=form.cleaned_data['execution_context']) |
                                     Q(ref_execution__ext_executor__icontains=form.cleaned_data['execution_context']) |
                                     Q(ref_execution__target__icontains=form.cleaned_data['execution_context']))
            if form.cleaned_data.get('card_context', False):
                search_result.filter(Q(ref_card__object_full_name__icontains=form.cleaned_data['card_context']) |
                                     Q(ref_card__doc_no__icontains=form.cleaned_data['card_context']) |
                                     Q(ref_card__doc_type__icontains=form.cleaned_data['card_context']) |
                                     Q(ref_card__doc_title__icontains=form.cleaned_data['card_context']) |
                                     Q(ref_card__doc_base__icontains=form.cleaned_data['card_context']))
            context['search_result'] = search_result
    else:
        form = ArchiveForm()
        context = {'form': form}
    return render(request, 'archive/index.html', context=context)
