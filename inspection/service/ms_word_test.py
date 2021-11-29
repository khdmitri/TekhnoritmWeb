import win32com.client as win32
# from win32com.client import Dispatch
from django.conf import settings
from datetime import datetime
import os
import io
import pythoncom
from django.http import HttpResponse


def gen_test():
    print(os.getcwd())
    template_path = settings.MEDIA_ROOT+'\\ms_templates\\'
    pythoncom.CoInitialize()
    try:
        wordApp = win32.gencache.EnsureDispatch('Word.Application') #create a word application object
        wordApp.Visible = True # hide the word application
        doc = wordApp.Documents.Open(template_path+"test.dotx")     # opening the template file
        #for creating a new one: doc = wordApp.Documents.Add()

        rng=doc.Bookmarks("doc_date").Range # change the string Name to whatever name of your bookmarks
        rng.InsertAfter(datetime.now().strftime('%d.%m.%Y'))
        rng=doc.Bookmarks("name").Range # change the string Name to whatever name of your bookmarks
        rng.InsertAfter('Text insert by bookmark "Name"')

        print('We have %s tables' % (doc.Tables.Count, ))  # change the string Name to whatever name of your bookmarks
        table_1 = doc.Tables(1)
        table_1.Cell(Row=1, Column=1).Range.Text='Row:1, Col:1'

        table_1.Cell(Row=2, Column=1).Merge(table_1.Cell(Row=2, Column=7))
        table_1.Cell(Row=2, Column=1).Range.Text='ВымпелКом'
        table_1.Cell(Row=2, Column=1).Range.ParagraphFormat.Alignment = 1 #win32.constants.wdAlignParagraphCenter
        table_1.Rows.Add()
        table_1.Rows.Add()
    # table_1.Rows(4).Delete()

        table_1.Cell(Row=4, Column=1).Split(1,7)

        file_path = template_path + "res.docx"
        doc.SaveAs(file_path, FileFormat=16)

        file_name = 'res_docx'
        file_size = os.path.getsize(file_path)
        length = file_size
        fsock = open(file_path, "rb")
        response = HttpResponse(
            fsock,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = 'attachment; filename='+file_name
        response['Content-Length'] = length

        # doc.SaveAs(template_path+"res.docx", FileFormat=16)
        # doc.SaveAs(template_path+"res.pdf", FileFormat=17)
        doc.Close()
        wordApp.Quit()
    finally:
        pythoncom.CoUninitialize()

    return response
