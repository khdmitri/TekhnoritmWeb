from .models import Card
from zipfile import ZipFile
from django.conf import settings
from io import BytesIO
from inspection.models import CommonObjectInfo, InspectionObject
from references.models import RequestPerson
import pythoncom
import win32com.client as win32
import os
from django.http import HttpResponse
import glob
from os.path import basename
from django.shortcuts import get_object_or_404
from .models import Task, ExecutionPlan, Card
from archive.models import ArchiveObject
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from references.models import DefaultTasks

TEMPLATE_PATH = settings.MEDIA_ROOT + '\\ms_templates\\sez_request\\'
TEMPLATE_PATH_LETTER = settings.MEDIA_ROOT + '\\ms_templates\\letter_request\\'
TEMP_FILE_PATH = settings.MEDIA_ROOT + '\\temp\\'


def get_title_from_parent(parent, target):
    dt = DefaultTasks.get_obj_by_target(target)
    template = dt.title_template
    res = ''
    if template is not None:
        words = template.split()
        for word in words:
            if word.startswith('!#'):
                word = word.replace('!#', '')
                if hasattr(parent, word):
                    res += ' '+getattr(parent, word)
            else:
                res += ' '+word
    return res


def generate_sez_request(action):
    objects_ = Card.get_cards_by_action(action)
    order = action.ref_task.ref_order
    common_object = CommonObjectInfo.objects.get(ref_order=order)
    regional_settings = RequestPerson.get_request_by_region_client(order.region, common_object.ref_owner)
    file_like_object = BytesIO()
    zipObj = ZipFile(file_like_object, 'w')
    pythoncom.CoInitialize()
    try:
        template_name = TEMPLATE_PATH + order.region + regional_settings.template + 'SEZ.dotx'
        ind = 0
        doc = None
        wordApp = None
        for object_ in objects_:
            ind += 1
            try:
                wordApp = win32.gencache.EnsureDispatch('Word.Application')  # create a word application object
                wordApp.Visible = False  # hide the word application
                doc = wordApp.Documents.Open(template_name)

                rng = doc.Bookmarks("address").Range
                if regional_settings.regional_address:
                    rng.InsertAfter(regional_settings.regional_address)
                else:
                    rng.InsertAfter(common_object.ref_owner.address_1)

                rng = doc.Bookmarks("inn").Range
                rng.InsertAfter(common_object.ref_owner.inn)

                rng = doc.Bookmarks("ogrn").Range
                rng.InsertAfter(common_object.ref_owner.ogrn)

                rng = doc.Bookmarks("owner").Range
                rng.InsertAfter(common_object.ref_owner.long_name)

                rng = doc.Bookmarks("project_designer").Range
                rng.InsertAfter(common_object.ref_project.long_name)

                rng = doc.Bookmarks("project_designer_address").Range
                rng.InsertAfter(common_object.ref_project.address_1)

                rng = doc.Bookmarks("project_name").Range
                rng.InsertAfter(object_.doc_base)

                rng = doc.Bookmarks("see_date").Range
                rng.InsertAfter(object_.doc_date.strftime('%d.%m.%Y'))

                rng = doc.Bookmarks("see_no").Range
                rng.InsertAfter(object_.doc_no)

                rng = doc.Bookmarks("sign_person").Range
                rng.InsertAfter(regional_settings.sign_person)

                rng = doc.Bookmarks("sign_position").Range
                rng.InsertAfter(regional_settings.sign_position)

                doc.SaveAs(TEMP_FILE_PATH + 'sez_'+str(ind), FileFormat=16)

                full_path = TEMP_FILE_PATH + 'sez_'+str(ind)+'.docx'
                zipObj.write(full_path, basename(full_path))
            except Exception as e:
                print('An error occured when processing object:', str(e))

        if doc is not None:
            doc.Close()
        if wordApp is not None:
            wordApp.Quit()

    except Exception as e:
        print('An error while processing objects in sez-request:', str(e))
    finally:
        pythoncom.CoUninitialize()
        zipObj.close()
        file_list = glob.glob(TEMP_FILE_PATH + 'sez_*')
        for file_path in file_list:
            os.remove(file_path)

    response = HttpResponse(content_type="application/zip")
    response["Content-Disposition"] = "attachment; filename=sez_requests.zip"

    file_like_object.seek(0)
    response.write(file_like_object.read())

    return response


def generate_letter_request(action):
    objects_ = Card.get_cards_by_action(action)
    order = action.ref_task.ref_order
    common_object = CommonObjectInfo.objects.get(ref_order=order)
    regional_settings = RequestPerson.get_request_by_region_client(order.region, common_object.ref_owner)
    file_like_object = BytesIO()
    zipObj = ZipFile(file_like_object, 'w')
    pythoncom.CoInitialize()
    try:
        template_name = TEMPLATE_PATH_LETTER + order.region + regional_settings.template + 'LETTER.dotx'
        ind = 0
        doc = None
        wordApp = None
        for object_ in objects_:
            ind += 1
            card_proto = Card.get_card_by_object_target(object_.object_id, 'PROTOCOL')
            inspection_object = InspectionObject.objects.get(id=object_.object_id)
            try:
                wordApp = win32.gencache.EnsureDispatch('Word.Application')  # create a word application object
                wordApp.Visible = False  # hide the word application
                doc = wordApp.Documents.Open(template_name)

                rng = doc.Bookmarks("address").Range
                if regional_settings.regional_address:
                    rng.InsertAfter(regional_settings.regional_address)
                else:
                    rng.InsertAfter(common_object.ref_owner.address_1)

                rng = doc.Bookmarks("inn").Range
                rng.InsertAfter(common_object.ref_owner.inn)

                rng = doc.Bookmarks("ogrn").Range
                rng.InsertAfter(common_object.ref_owner.ogrn)

                rng = doc.Bookmarks("owner").Range
                rng.InsertAfter(common_object.ref_owner.long_name)

                rng = doc.Bookmarks("project_designer").Range
                rng.InsertAfter(common_object.ref_project.long_name)

                rng = doc.Bookmarks("project_designer_address").Range
                rng.InsertAfter(common_object.ref_project.address_1)

                rng = doc.Bookmarks("ez_date").Range
                rng.InsertAfter(object_.doc_date.strftime('%d.%m.%Y'))

                rng = doc.Bookmarks("ez_no").Range
                rng.InsertAfter(object_.doc_no)

                if card_proto is not None:
                    rng = doc.Bookmarks("proto_date").Range
                    rng.InsertAfter(card_proto.doc_date.strftime('%d.%m.%Y'))

                    rng = doc.Bookmarks("proto_no").Range
                    rng.InsertAfter(card_proto.doc_no)

                if inspection_object:
                    rng = doc.Bookmarks("location").Range
                    rng.InsertAfter(inspection_object.address)

                rng = doc.Bookmarks("prto_full_name").Range
                rng.InsertAfter(object_.object_full_name)

                rng = doc.Bookmarks("sign_person").Range
                rng.InsertAfter(regional_settings.sign_person)

                rng = doc.Bookmarks("sign_position").Range
                rng.InsertAfter(regional_settings.sign_position)

                doc.SaveAs(TEMP_FILE_PATH + 'letter_'+str(ind), FileFormat=16)

                full_path = TEMP_FILE_PATH + 'letter_'+str(ind)+'.docx'
                zipObj.write(full_path, basename(full_path))
            except Exception as e:
                print('An error occurs when processing object:', str(e))

        if doc is not None:
            doc.Close()
        if wordApp is not None:
            wordApp.Quit()

    except Exception as e:
        print('An error while processing objects in letter-request:', str(e))
    finally:
        pythoncom.CoUninitialize()
        zipObj.close()
        file_list = glob.glob(TEMP_FILE_PATH + 'letter_*')
        for file_path in file_list:
            os.remove(file_path)

    response = HttpResponse(content_type="application/zip")
    response["Content-Disposition"] = "attachment; filename=letter_requests.zip"

    file_like_object.seek(0)
    response.write(file_like_object.read())

    return response

