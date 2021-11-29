from celery import shared_task
from celery_progress.backend import ProgressRecorder
from .models import Task, ExecutionPlan, Card
from archive.models import ArchiveObject
import pythoncom
import win32com.client as win32
from django.shortcuts import get_object_or_404
import time


def get_doc_context(path):
    text_content = ''
    pythoncom.CoInitialize()
    try:
        wordApp = win32.gencache.EnsureDispatch('Word.Application')  # create a word application object
        wordApp.Visible = False  # hide the word application
        doc = wordApp.Documents.Open(path)
        text_content = doc.Content.Text
    except Exception as e:
        print(str(e))
        return {'success': False, 'error': str(e)}
    finally:
        try:
            doc.Close()
            wordApp.Quit()
        except:
            pass
        pythoncom.CoUninitialize()

    return {'success': True, 'text': text_content}


def valid_word_file(file):
    import os
    if file:
        ext = os.path.splitext(file.name)[1]
        valid_extensions = ['.doc', '.docx']
        if ext.lower() in valid_extensions:
            return True
    return False

@shared_task(bind=True)
def make_archive(self, model_task_id):
    task = get_object_or_404(Task, task_id=model_task_id)
    executions = ExecutionPlan.get_actions_by_task(task)
    card_list = []

    progress_recorder = ProgressRecorder(self)
    result = 0

    for action in executions:
        new_cards = list(Card.get_cards_by_action(action))
        if len(new_cards)>0:
            card_list += new_cards

    if len(card_list) > 0:
        for card in card_list:
            result += 1
            print('Iteration:', result)
            print('Card id:', card.execution_id)
            progress_recorder.set_progress(result, len(card_list))
            newArchiveObject = ArchiveObject(
                ref_order=card.ref_action.ref_task.ref_order,
                ref_task=card.ref_action.ref_task,
                ref_execution=card.ref_action,
                ref_card=card
            )
            newArchiveObject.save()
            print('Card successfully saved!')
            try:
                if valid_word_file(card.source_file):
                    text_content = get_doc_context(card.source_file.path)
                    if text_content['success']:
                        newArchiveObject.doc_context = text_content['text']
                    else:
                        newArchiveObject.doc_context = ''
                newArchiveObject.save()
            except Exception as e:
                print('An error when get file content:', str(e))
    print('For ended!')
    return len(card_list)


@shared_task(bind=True)
def my_task(self, seconds):
    progress_recorder = ProgressRecorder(self)
    result = 0
    for i in range(seconds):
        time.sleep(1)
        result += 1
        progress_recorder.set_progress(i + 1, seconds)
        print(result)
    print('Summary:', result)
    return result
