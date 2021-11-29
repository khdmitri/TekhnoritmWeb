from django.core.files import File
from os.path import basename
from tempfile import TemporaryFile
from urllib.parse import urlsplit
import win32com.client as win32
import pythoncom
from django.core.files.storage import default_storage
import os
import subprocess
from django.conf import settings


SIGN_CONFIG = {
    'sign_stamp': '0c8240bd6bbda587dbdf6b750d55d4ee9ce66103',
}


def ms_word_to_pdf(file_stream):
    path = default_storage.save(file_stream.name, file_stream)
    pythoncom.CoInitialize()

    try:
        wordApp = win32.gencache.EnsureDispatch('Word.Application')  # create a word application object
        wordApp.Visible = False  # hide the word application
        doc = wordApp.Documents.Open(os.path.join(default_storage.location, path))

        doc.SaveAs(os.path.join(default_storage.location, path+'.pdf'), FileFormat=17)
        doc.Close()
        wordApp.Quit()
    except Exception as e:
        return {'success': False, 'error': str(e)}
    finally:
        pythoncom.CoUninitialize()

    return {'success': True, 'file_path': path}


def sign_doc(in_file):
    try:
        subprocess.run([settings.PATH_TO_SIGN_TOOL, '-sfsign', '-sign', '-my', SIGN_CONFIG['sign_stamp'], '-in', in_file.path, '-out', in_file.path+'.sig'])
        res = {'success': True, 'out_file': in_file.path + '.sig', 'out_file_name': in_file.name+'.sig'}
    except Exception as e:
        res = {'success': False, 'error': str(e)}

    return res
