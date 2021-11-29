from celery import shared_task
from celery_progress.backend import ProgressRecorder
from .service import parse_rpn_letter


@shared_task(bind=True)
def upload_rpn_files(self, files):
    progress_recorder = ProgressRecorder(self)
    result = 0
    for f in files:
        result += 1
        res = parse_rpn_letter(f)
        print('Iteration-%s: %s' % (result, res,))
        progress_recorder.set_progress(result, len(files))

    return result
