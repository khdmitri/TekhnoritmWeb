from inspection.models import SEE, SourceData, IncomeDocument, EvalPoints, DocumentLow, DocumentSign, CommonObjectInfo
from references.models import RequestPerson
from django.shortcuts import get_object_or_404
import calendar
import time
from django.conf import settings
import win32com.client as win32
import pythoncom
from django.http import HttpResponse
import os
from datetime import datetime
from itertools import groupby
from operator import attrgetter
from django.utils import translation


def generate(ref_object):
    sd = SourceData.get_data_by_object(ref_object)
    see = get_object_or_404(SEE, ref_object=ref_object)
    order = ref_object.ref_order
    common_info = get_object_or_404(CommonObjectInfo, ref_order=ref_object.ref_order)
    regional_settings = RequestPerson.get_request_by_region_client(order.region, common_info.ref_owner)
    income_documents = IncomeDocument.get_docs_by_see(see)
    eval_points = EvalPoints.get_points_by_see(see)
    low_evals = DocumentLow.get_items_by_types('see', 'evals')
    low_methods = DocumentLow.get_items_by_types('see', 'methods')
    doc_sign_approved = DocumentSign.get_sign_by_types('see', 'approved')
    doc_sign_sign = DocumentSign.get_sign_by_types('see', 'sign')

    prto_name = ref_object.prto_type_ref.name_visible+' '+ref_object.name
    sharing = ''
    if ref_object.is_shared:
        sharing_name = ref_object.shared_name if isinstance(ref_object.shared_name, str) else ""
        sharing_standart = ref_object.shared_standard if isinstance(ref_object.shared_standard, str) else ""
        sharing_owner = ref_object.shared_owner if isinstance(ref_object.shared_owner, str) else ""
        sharing = ' совместно с (sharing) '+sharing_name+\
                     ' по стандартам '+sharing_standart+' '+sharing_owner

    ts = calendar.timegm(time.gmtime())
    file_name = str(ts)+'_see.docx'
    print(file_name)

    template_path = settings.MEDIA_ROOT + '\\ms_templates\\see\\'
    temp_files_path = settings.MEDIA_ROOT + '\\temp\\'

    pythoncom.CoInitialize()
    try:
        wordApp = win32.gencache.EnsureDispatch('Word.Application')  # create a word application object
        wordApp.Visible = False  # hide the word application
        doc = wordApp.Documents.Open(template_path + "see.dotx")

        rng = doc.Bookmarks("approve_pos").Range
        rng.InsertAfter(doc_sign_approved.ref_person.profile.get_position())

        rng = doc.Bookmarks("approve_sign").Range
        rng.InsertAfter(doc_sign_approved.ref_person.profile.initials+' '+doc_sign_approved.ref_person.last_name)

        now = datetime.now()

        rng = doc.Bookmarks("cur_dd").Range
        rng.InsertAfter(now.strftime('%d'))

        rng = doc.Bookmarks("cur_mm").Range
        translation.activate('ru')
        rng.InsertAfter(now.strftime('%m'))

        rng = doc.Bookmarks("cur_yyyy").Range
        rng.InsertAfter(now.strftime('%Y'))

        rng = doc.Bookmarks("doc_date").Range
        rng.InsertAfter(see.see_date.strftime('%d.%m.%Y'))

        rng = doc.Bookmarks("doc_no").Range
        rng.InsertAfter(see.see_no)

        rng = doc.Bookmarks("order").Range
        rng.InsertAfter('No.:'+order.order_id+' от '+order.create_date.strftime('%d.%m.%Y'))

        full_prto_name = prto_name + ' ' + see.standard + ' принадлежащий '+ common_info.ref_owner.short_name + sharing

        rng = doc.Bookmarks("prto_name").Range
        rng.InsertAfter(full_prto_name)

        rng = doc.Bookmarks("prto_name2").Range
        rng.InsertAfter(prto_name)

        rng = doc.Bookmarks("prto_name3").Range
        rng.InsertAfter(full_prto_name)

        rng = doc.Bookmarks("prto_name4").Range
        rng.InsertAfter(full_prto_name)

        rng = doc.Bookmarks("prto_name5").Range
        rng.InsertAfter(full_prto_name)

        rng = doc.Bookmarks("standard").Range
        rng.InsertAfter(see.standard)

        rng = doc.Bookmarks("standard2").Range
        rng.InsertAfter(see.standard)

        rng = doc.Bookmarks("owner2").Range
        rng.InsertAfter(common_info.ref_owner.short_name)

        rng = doc.Bookmarks("owner_full_name").Range
        rng.InsertAfter(common_info.ref_owner.long_name)

        rng = doc.Bookmarks("owner_full_name3").Range
        rng.InsertAfter(common_info.ref_owner.long_name)

        rng = doc.Bookmarks("address_ur").Range
        rng.InsertAfter(common_info.ref_owner.address_1)

        rng = doc.Bookmarks("address_fact").Range
        if regional_settings is not None and regional_settings.regional_address:
            rng.InsertAfter(regional_settings.regional_address)
        else:
            rng.InsertAfter(common_info.ref_owner.address_2)

        rng = doc.Bookmarks("address_ur2").Range
        rng.InsertAfter(common_info.ref_owner.address_1)

        rng = doc.Bookmarks("address_fact2").Range
        if regional_settings and regional_settings.regional_address:
            rng.InsertAfter(regional_settings.regional_address)
        else:
            rng.InsertAfter(common_info.ref_owner.address_2)

        rng = doc.Bookmarks("location").Range
        rng.InsertAfter(ref_object.address)

        rng = doc.Bookmarks("build_year").Range
        rng.InsertAfter(str(ref_object.build_year))

        rng = doc.Bookmarks("build_purpose").Range
        rng.InsertAfter(str(ref_object.build_purpose))

        rng = doc.Bookmarks("project_header").Range
        rng.InsertAfter(see.project_header)

        rng = doc.Bookmarks("project_designer").Range
        str_designer = common_info.ref_project.short_name + ', ' + common_info.ref_project.address_1 + ' (ИНН:' + \
              common_info.ref_project.inn + ', ОГРН:' + common_info.ref_project.ogrn + ')'
        rng.InsertAfter(str_designer)

        rng = doc.Bookmarks("freq").Range
        rng.InsertAfter(see.freq)

        rng = doc.Bookmarks("pdu_staff").Range
        rng.InsertAfter(ref_object.prto_type_ref.pdu_staff)

        rng = doc.Bookmarks("pdu_common").Range
        rng.InsertAfter(ref_object.prto_type_ref.pdu_common)

        table_eval = doc.Tables(5)
        row=0
        evals_str = ''
        for low_eval in low_evals:
            row += 1
            if row > 1:
                table_eval.Rows.Add()
                evals_str += '\n-' + low_eval.low_notation + ' ' + low_eval.low_name
            else:
                evals_str += '-' + low_eval.low_notation + ' ' + low_eval.low_name
            table_eval.Cell(Row=row, Column=1).Range.Text = '-'
            table_eval.Cell(Row=row, Column=2).Range.Text = low_eval.low_notation+' '+low_eval.low_name

        table_eval = doc.Tables(9)
        row = 0
        evals_str = ''
        for low_eval in low_evals:
            row += 1
            if row > 1:
                table_eval.Rows.Add()
                evals_str += '\n-' + low_eval.low_notation + ' ' + low_eval.low_name
            else:
                evals_str += '-' + low_eval.low_notation + ' ' + low_eval.low_name
            table_eval.Cell(Row=row, Column=1).Range.Text = '-'
            table_eval.Cell(Row=row, Column=2).Range.Text = low_eval.low_notation + ' ' + low_eval.low_name

        rng = doc.Bookmarks("doc_evals").Range
        rng.InsertAfter(evals_str)

        rng = doc.Bookmarks("az").Range
        rng.InsertAfter(see.az)

        rng = doc.Bookmarks("az2").Range
        rng.InsertAfter(see.az)

        rng = doc.Bookmarks("szz").Range
        if see.szz_description is None:
            see.szz_description = ''
        rng.InsertAfter(see.szz_description)

        rng = doc.Bookmarks("zoz").Range
        if see.zoz_description is None:
            see.zoz_description = ''
        rng.InsertAfter(see.zoz_description)

        rng = doc.Bookmarks("extra").Range
        if see.extra is None:
            see.extra = ''
        if see.extra_staff is None:
            see.extra_staff = ''
        rng.InsertAfter(see.extra+'\n'+see.extra_staff)

        rng = doc.Bookmarks("sign_pos").Range
        rng.InsertAfter(doc_sign_sign.ref_person.profile.get_position())

        rng = doc.Bookmarks("sign_sign").Range
        rng.InsertAfter(doc_sign_sign.ref_person.profile.initials + ' ' + doc_sign_sign.ref_person.last_name)

        table_method = doc.Tables(6)
        row = 0
        for low_method in low_methods:
            row += 1
            if row > 1:
                table_eval.Rows.Add()
            table_method.Cell(Row=row, Column=1).Range.Text = '-'
            table_method.Cell(Row=row, Column=2).Range.Text = low_method.low_notation + ' ' + low_method.low_name

        table_data = doc.Tables(2)
        sd_1 = sd.filter(kind_code=1)
        row=1
        title_posted = False
        for sd_el in sd_1:
            row += 1
            table_data.Rows.Add()
            if not title_posted:
                title_posted = True
                table_data.Cell(Row=row, Column=1).Merge(table_data.Cell(Row=row, Column=11))
                table_data.Cell(Row=row, Column=1).Range.Text = sd_el.kind_description
                table_data.Cell(Row=row, Column=1).Range.ParagraphFormat.Alignment = 1
                table_data.Cell(Row=row, Column=1).Range.Font.Bold = True
                row += 1
            table_data.Cell(Row=row, Column=1).Range.Text = sd_el.row_type
            table_data.Cell(Row=row, Column=2).Range.Text = sd_el.power
            table_data.Cell(Row=row, Column=3).Range.Text = sd_el.qty
            table_data.Cell(Row=row, Column=4).Range.Text = sd_el.freq
            if sd_el.modulation is None:
                sd_el.modulation = ''
            table_data.Cell(Row=row, Column=5).Range.Text = sd_el.modulation
            table_data.Cell(Row=row, Column=6).Range.Text = sd_el.antenna
            table_data.Cell(Row=row, Column=7).Range.Text = sd_el.gain
            table_data.Cell(Row=row, Column=8).Range.Text = sd_el.high
            table_data.Cell(Row=row, Column=9).Range.Text = sd_el.power_fact
            table_data.Cell(Row=row, Column=10).Range.Text = sd_el.dn
            table_data.Cell(Row=row, Column=11).Range.Text = sd_el.az_hor+'/'+sd_el.az_vert

        sd_2 = sd.filter(kind_code=2)
        title_posted = False
        for sd_el in sd_2:
            row += 1
            table_data.Rows.Add()
            if not title_posted:
                title_posted = True
                table_data.Rows.Add()
                table_data.Cell(Row=row, Column=1).Merge(table_data.Cell(Row=row, Column=11))
                table_data.Cell(Row=row, Column=1).Range.Text = sd_el.kind_description
                table_data.Cell(Row=row, Column=1).Range.ParagraphFormat.Alignment = 1
                table_data.Cell(Row=row, Column=1).Range.Font.Bold = True
                row += 1
            table_data.Cell(Row=row, Column=1).Range.Text = sd_el.row_type
            table_data.Cell(Row=row, Column=2).Range.Text = sd_el.power
            table_data.Cell(Row=row, Column=3).Range.Text = sd_el.qty
            table_data.Cell(Row=row, Column=4).Range.Text = sd_el.freq
            if sd_el.modulation is None:
                sd_el.modulation = ''
            table_data.Cell(Row=row, Column=5).Range.Text = sd_el.modulation
            table_data.Cell(Row=row, Column=6).Range.Text = sd_el.antenna
            table_data.Cell(Row=row, Column=7).Range.Text = sd_el.gain
            table_data.Cell(Row=row, Column=8).Range.Text = sd_el.high
            table_data.Cell(Row=row, Column=9).Range.Text = sd_el.power_fact
            table_data.Cell(Row=row, Column=10).Range.Text = sd_el.dn
            table_data.Cell(Row=row, Column=11).Range.Text = sd_el.az_hor+'/'+sd_el.az_vert

        sd_3 = sd.filter(kind_code=3).order_by('ref_owner')
        row += 1
        table_data.Rows.Add()
        table_data.Rows.Add()
        table_data.Cell(Row=row, Column=1).Merge(table_data.Cell(Row=row, Column=11))
        table_data.Cell(Row=row, Column=1).Range.Text = 'Стороннее оборудование'
        table_data.Cell(Row=row, Column=1).Range.ParagraphFormat.Alignment = 1
        table_data.Cell(Row=row, Column=1).Range.Font.Bold = True
        row += 1
        if sd_3:
            rows = groupby(sd_3, key=attrgetter('ref_owner'))
            for title, items in rows:
                table_data.Rows.Add()
                table_data.Cell(Row=row, Column=1).Merge(table_data.Cell(Row=row, Column=11))
                if hasattr(title, 'short_name'):
                    table_data.Cell(Row=row, Column=1).Range.Text = title.short_name
                else:
                    table_data.Cell(Row=row, Column=1).Range.Text = ""
                table_data.Cell(Row=row, Column=1).Range.ParagraphFormat.Alignment = 1
                table_data.Cell(Row=row, Column=1).Range.Font.Italic = True
                first_row = True
                for item in items:
                    row += 1
                    if not first_row:
                        table_data.Rows.Add()
                    table_data.Cell(Row=row, Column=1).Range.Text = item.row_type
                    table_data.Cell(Row=row, Column=2).Range.Text = item.power
                    table_data.Cell(Row=row, Column=3).Range.Text = item.qty
                    table_data.Cell(Row=row, Column=4).Range.Text = item.freq
                    if item.modulation is None:
                        item.modulation = ''
                    table_data.Cell(Row=row, Column=5).Range.Text = item.modulation
                    table_data.Cell(Row=row, Column=6).Range.Text = item.antenna
                    table_data.Cell(Row=row, Column=7).Range.Text = item.gain
                    table_data.Cell(Row=row, Column=8).Range.Text = item.high
                    table_data.Cell(Row=row, Column=9).Range.Text = item.power_fact
                    table_data.Cell(Row=row, Column=10).Range.Text = item.dn
                    table_data.Cell(Row=row, Column=11).Range.Text = item.az_hor + '/' + item.az_vert
                    first_row = False
        else:
            table_data.Cell(Row=row, Column=1).Merge(table_data.Cell(Row=row, Column=11))
            table_data.Cell(Row=row, Column=1).Range.Text = 'Отсутствует'
            table_data.Cell(Row=row, Column=1).Range.ParagraphFormat.Alignment = 1
            table_data.Cell(Row=row, Column=1).Range.Font.Italic = True

        table_income_doc = doc.Tables(1)
        row=0
        for income_doc in income_documents:
            row += 1
            if row > 1:
                table_income_doc.Rows.Add()
            table_income_doc.Cell(Row=row, Column=1).Range.Text = '-'
            table_income_doc.Cell(Row=row, Column=2).Range.Text = income_doc.presentation

        table_point = doc.Tables(4)
        row=1
        for point in eval_points:
            row += 1
            if row > 2:
                table_point.Rows.Add()
            table_point.Cell(Row=row, Column=1).Range.Text = point.no
            table_point.Cell(Row=row, Column=2).Range.Text = point.place
            table_point.Cell(Row=row, Column=3).Range.Text = point.no_plan
            if point.unit is None:
                point.unit = 'мкВт/см2'
                point.save()
            table_point.Cell(Row=row, Column=4).Range.Text = point.value+point.unit
            table_point.Cell(Row=row, Column=5).Range.Text = point.distance
            table_point.Cell(Row=row, Column=6).Range.Text = point.high
            table_point.Cell(Row=row, Column=7).Range.Text = point.az

        doc.SaveAs(temp_files_path+file_name, FileFormat=16)

        file_size = os.path.getsize(temp_files_path+file_name)
        length = file_size
        fsock = open(temp_files_path+file_name, "rb")
        response = HttpResponse(
            fsock,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename=' + file_name
        response['Content-Length'] = length

        # doc.SaveAs(template_path+"res.docx", FileFormat=16)
        # doc.SaveAs(template_path+"res.pdf", FileFormat=17)
        doc.Close()
        wordApp.Quit()
    finally:
        pythoncom.CoUninitialize()

    return response
