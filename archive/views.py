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
            if form.from_date:
                search_result.filter(from_date__gte=form.from_date)
            if form.to_date:
                search_result.filter(to_date__lte=form.to_date)
            if form.order_context:
                search_result.filter(Q(ref_order__order_id__icontains=form.order_context) |
                                     Q(ref_order__ext_order_id__icontains=form.order_context) |
                                     Q(ref_order__client__short_name__icontains=form.order_context) |
                                     Q(ref_order__client__long_name__icontains=form.order_context) |
                                     Q(ref_order__region__contains=form.order_context))
            if form.task_context:
                search_result.filter(Q(ref_task__task_id__contains=form.task_context) |
                                     Q(ref_task__distribution_dep__description__icontains=form.task_context) |
                                     Q(ref_task__distribution_dep__name__contains=form.task_context) |
                                     Q(ref_task__task_type__contains=form.task_context))
            if form.execution_context:
                search_result.filter(Q(ref_execution__int_executor__description__icontains=form.execution_context) |
                                     Q(ref_execution__int_executor__name__icontains=form.execution_context) |
                                     Q(ref_execution__ext_executor__icontains=form.execution_context) |
                                     Q(ref_execution__target__icontains=form.execution_context))
            if form.card_context:
                search_result.filter(Q(ref_card__object_full_name__icontains=form.card_context) |
                                     Q(ref_card__doc_no__icontains=form.card_context) |
                                     Q(ref_card__doc_type__icontains=form.card_context) |
                                     Q(ref_card__doc_title__icontains=form.card_context) |
                                     Q(ref_card__doc_base__icontains=form.card_context))
            context['search_result'] = search_result
    else:
        form = ArchiveForm()
        context = {'form': form}
    return render(request, 'archive/index.html', context=context)
