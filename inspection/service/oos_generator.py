from inspection.models import SEE, SourceData, IncomeDocument, EvalPoints, DocumentLow, DocumentSign, CommonObjectInfo
from references.models import RequestPerson
from django.shortcuts import render, get_object_or_404
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


def generate_oos(ref_object):
    sd = SourceData.get_data_by_object(ref_object)
    see = get_object_or_404(SEE, ref_object=ref_object)
    order = ref_object.ref_order
    common_info = get_object_or_404(CommonObjectInfo, ref_order=ref_object.ref_order)
    regional_settings = RequestPerson.get_request_by_region_client(order.region, common_info.ref_owner)
    doc_sign_sign = DocumentSign.get_sign_by_types('oos', 'sign')

    prto_name = ref_object.prto_type_ref.name_visible+' '+ref_object.name

    ts = calendar.timegm(time.gmtime())
    file_name = str(ts)+'_oos.docx'
    print(file_name)

    template_path = settings.MEDIA_ROOT + '\\ms_templates\\oos\\'
    temp_files_path = settings.MEDIA_ROOT + '\\temp\\'

    pythoncom.CoInitialize()
    try:
        wordApp = win32.gencache.EnsureDispatch('Word.Application')  # create a word application object
        wordApp.Visible = False  # hide the word application
        doc = wordApp.Documents.Open(template_path + "oos.dotx")

        now = datetime.now()

        rng = doc.Bookmarks("region").Range
        rng.InsertAfter(ref_object.ref_order.region)

        rng = doc.Bookmarks("cur_yyyy").Range
        rng.InsertAfter(now.strftime('%Y'))

        rng = doc.Bookmarks("prto_name2").Range
        rng.InsertAfter(prto_name)

        rng = doc.Bookmarks("standard").Range
        rng.InsertAfter(see.standard)

        sharing = ''
        if ref_object.is_shared:
            sharing = ' совместно с (sharing) ' + ref_object.shared_name + \
                      ' по стандартам ' + ref_object.shared_standard + ' ' + ref_object.shared_owner

        rng = doc.Bookmarks("owner").Range
        rng.InsertAfter(common_info.ref_owner.short_name + sharing)

        rng = doc.Bookmarks("owner_full_name").Range
        rng.InsertAfter(common_info.ref_owner.long_name)

        rng = doc.Bookmarks("address_ur").Range
        rng.InsertAfter(common_info.ref_owner.address_1)

        rng = doc.Bookmarks("address_fact").Range
        if regional_settings is not None and regional_settings.regional_address:
            rng.InsertAfter(regional_settings.regional_address)
        else:
            rng.InsertAfter(common_info.ref_owner.address_2)

        rng = doc.Bookmarks("location").Range
        rng.InsertAfter(ref_object.address)

        rng = doc.Bookmarks("build_year").Range
        rng.InsertAfter(str(ref_object.build_year))

        rng = doc.Bookmarks("build_purpose").Range
        rng.InsertAfter(str(ref_object.build_purpose))

        rng = doc.Bookmarks("sign_pos").Range
        rng.InsertAfter(doc_sign_sign.ref_person.profile.get_position())

        rng = doc.Bookmarks("sign_sign").Range
        rng.InsertAfter(doc_sign_sign.ref_person.profile.initials + ' ' + doc_sign_sign.ref_person.last_name)

        table_data = doc.Tables(2)
        sd_1 = sd.filter(kind_code=1)
        row=1
        title_posted = False
        for sd_el in sd_1:
            row += 1
            table_data.Rows.Add()
            if not title_posted:
                title_posted = True
                table_data.Cell(Row=row, Column=1).Merge(table_data.Cell(Row=row, Column=10))
                table_data.Cell(Row=row, Column=1).Range.Text = sd_el.kind_description
                table_data.Cell(Row=row, Column=1).Range.ParagraphFormat.Alignment = 1
                table_data.Cell(Row=row, Column=1).Range.Font.Bold = True
                row += 1
            if sd_el.row_type:
                table_data.Cell(Row=row, Column=1).Range.Text = sd_el.row_type
            if sd_el.power:
                table_data.Cell(Row=row, Column=2).Range.Text = sd_el.power
            if sd_el.qty:
                table_data.Cell(Row=row, Column=3).Range.Text = sd_el.qty
            if sd_el.freq:
                table_data.Cell(Row=row, Column=4).Range.Text = sd_el.freq
            if sd_el.modulation:
                table_data.Cell(Row=row, Column=5).Range.Text = sd_el.modulation
            if sd_el.antenna:
                table_data.Cell(Row=row, Column=6).Range.Text = sd_el.antenna
            if sd_el.gain:
                table_data.Cell(Row=row, Column=7).Range.Text = sd_el.gain
            if sd_el.high:
                table_data.Cell(Row=row, Column=8).Range.Text = sd_el.high
            if sd_el.power_fact:
                table_data.Cell(Row=row, Column=9).Range.Text = sd_el.power_fact
            if sd_el.dn:
                table_data.Cell(Row=row, Column=10).Range.Text = sd_el.dn
            if sd_el.az_hor and sd_el.az_vert:
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
