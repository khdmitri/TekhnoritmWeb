import os
import platform
from django.core.files.storage import default_storage
from django.core.files import File
from django.conf import settings
import win32com.client as win32
import pythoncom
from .models import RPNLetter
import re
import datetime


def creation_date(path_to_file):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def parse_rpn_letter(file_stream):
    path = default_storage.save(file_stream.name, file_stream)
    pythoncom.CoInitialize()
    try:
        wordApp = win32.gencache.EnsureDispatch('Word.Application')  # create a word application object
        wordApp.Visible = False  # hide the word application
        doc = wordApp.Documents.Open(os.path.join(default_storage.location, path))

        letter_model = RPNLetter.objects.create()
        letter_model.attach.save(path,
                                 File(default_storage.open(path)),
                                 save=True)
        letter_model.orig_file_name = file_stream.name
        letter_model.text_content = doc.Content.Text
        doc_date = re.search(r'[\d]{1,2}\.[\d]{1,2}\.[\d]{2,4}', letter_model.text_content)
        if doc_date.group:
            print(doc_date.group(0))
            try:
                letter_model.file_create_date = datetime.datetime.strptime(doc_date.group(0),"%d.%m.%Y")
            except:
                letter_model.file_create_date = datetime.datetime.strptime(doc_date.group(0), "%d.%m.%y")
        letter_model.save()
    except Exception as e:
        print(str(e))
        return {'success': False, 'error': str(e)}
    finally:
        try:
            doc.Close()
            wordApp.Quit()
            default_storage.delete(path)
        except:
            pass
        pythoncom.CoUninitialize()

    return {'success': True}
