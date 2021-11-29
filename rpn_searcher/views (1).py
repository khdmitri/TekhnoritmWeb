from django.shortcuts import render
from .forms import UploadFilesForm
from .models import RPNLetter
from django.contrib.auth.decorators import permission_required
from .service import creation_date, parse_rpn_letter
from django.db.models import Q


@permission_required('accounts.can_upload_rpn_files')
def show_upload_page(request):
    form = UploadFilesForm()
    context = {
        'form': form
    }

    return render(request, 'rpn_searcher/upload_letters.html', context)


def upload_post(request):
    if request.method == 'POST':
        files = request.FILES.getlist('file_field')
        i = 0
        for f in files:
            i += 1
            res = parse_rpn_letter(f)
            if res['success']:
                context = {
                    'current': i,
                    'total': len(files)
                }
    context = {
        'success': True,
    }
    return render(request, 'rpn_searcher/process_counter.html', context)


def ajax_search_list(request):
    search_line = request.GET['search_line']
    if search_line:
        letters = RPNLetter.objects.filter(Q(text_content__icontains=search_line) | Q(
                                             orig_file_name__icontains=search_line)).order_by('-file_create_date')[:20]
    else:
        letters = None
    context = {
        'letters': letters,
    }
    return render(request, 'rpn_searcher/rpn_list_ajax.html', context)


def search_rpn(request):
    return render(request, 'rpn_searcher/letter_list.html')
