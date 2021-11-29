from django.shortcuts import render
from .forms import UploadFilesForm
from .models import RPNLetter
from django.contrib.auth.decorators import permission_required
from .service import creation_date, parse_rpn_letter
from django.db.models import Q
from accounts.choices import USER_REGION
from functools import reduce
from operator import and_
from .tasks import upload_rpn_files


@permission_required('accounts.can_upload_rpn_files')
def show_upload_page(request):
    form = UploadFilesForm()
    context = {
        'form': form
    }

    return render(request, 'rpn_searcher/upload_letters.html', context)


def upload_post(request):
    context = {}
    if request.method == 'POST':
        files = request.FILES.getlist('file_field')
        result = upload_rpn_files.delay(files)
        context = {
            'show_progress': True,
            'task_id': result.task_id,
        }
    return render(request, 'rpn_searcher/upload_letters.html', context)


def ajax_search_list(request):
    search_line = request.GET['search_line']
    type_search = request.GET['type_search']
    region = request.GET['region']
    if search_line:
        region_qs = None
        if region != '0':
            region_qs = reduce(and_, (Q(source_region__icontains=region), ))
        if type_search == 'strong':
            if region_qs is not None:
                letters = RPNLetter.objects.filter(Q(text_content__icontains=search_line) | Q(
                                                     orig_file_name__icontains=search_line)).filter(region_qs).order_by(
                                                     '-file_create_date')[:20]
            else:
                letters = RPNLetter.objects.filter(Q(text_content__icontains=search_line) | Q(
                    orig_file_name__icontains=search_line)).order_by(
                    '-file_create_date')[:20]
        else:
            tag_qs = reduce(and_, (Q(text_content__icontains=x) for x in search_line.split()))
            print('QS:', tag_qs)
            if region_qs is not None:
                letters = RPNLetter.objects.filter(tag_qs).filter(region_qs).order_by('-file_create_date')[:20]
            else:
                letters = RPNLetter.objects.filter(tag_qs).order_by('-file_create_date')[:20]

    else:
        letters = None
    context = {
        'letters': letters,
        'regions': USER_REGION,
    }
    return render(request, 'rpn_searcher/rpn_list_ajax.html', context)


def search_rpn(request):
    context = {
        'regions': USER_REGION
    }
    return render(request, 'rpn_searcher/letter_list.html', context)
