import json

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from export.forms import ExportProtocolForm, ProtocolAddressFiasForm
from export.service import XMLGenerator, DadataClient
from inspection.models import Protocol


def protocol_list(request):
    protocols = Protocol.objects.filter(
        export_date__isnull=True).filter(
        export_exclude=False).order_by('-protocol_date')[:30]
    if request.method == 'POST':
        form = ExportProtocolForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            protocol_ids = request.POST.getlist('protocol')
            if action == 'generate':
                xml_class = XMLGenerator()
                dadata_class = DadataClient()
                xml = xml_class.generate(dadata_class.update_protocols(protocol_ids))
                output = 'protocols.xml'
                response = HttpResponse(xml, content_type='application/xml')
                response['Content-Disposition'] = f'attachment; filename={output}'
                return response
            elif action == 'exclude':
                protocols = list()
                for p_id in protocol_ids:
                    protocol = Protocol.objects.get(protocol_id=p_id)
                    protocol.export_exclude = True
                    protocol.save()
                    protocols.append(protocol)
                messages.add_message(request, messages.INFO, f'Исключено из экспорта <strong>{len(protocols)}</strong> протоколов!')
                protocols = Protocol.objects.filter(
                    export_date__isnull=True).filter(
                    export_exclude=False).order_by('-protocol_date')[:30]
            elif action == 'select':
                try:
                    from_date = form.cleaned_data['from_date']
                    to_date = form.cleaned_data['to_date']
                    protocols = Protocol.objects.filter(protocol_date__range=(from_date, to_date))
                    messages.add_message(request, messages.INFO, f'Выбрано <strong>{len(protocols)}</strong> документов!')
                except Exception as e:
                    print(str(e))
                    raise ValidationError('Даты не корректны', code='dates_invalid')
    else:
        form = ExportProtocolForm(initial={
            'action': 'generate',
        })
    context = {
        'form': form,
        'protocols': protocols,
    }
    return render(request, 'export/protocol_list.html', context)


def protocol_address(request, protocol_id):
    protocol = get_object_or_404(Protocol, protocol_id=protocol_id)
    if request.method == 'POST':
        form = ProtocolAddressFiasForm(request.POST)
        if form.is_valid():
            address_fias = form.cleaned_data['address_fias']
            obj = protocol.ref_object
            obj.address_fias = json.loads(address_fias)
            obj.save()
            protocol.refresh_from_db()
            messages.add_message(request, messages.INFO, 'Адрес был успешно обновлен в соответствии с базой ФИАС')
    else:
        form = ProtocolAddressFiasForm(initial={
            'protocol_id': protocol.protocol_id,
            'address': protocol.ref_object.address
        })

    context = {
        'form': form,
        'protocol': protocol,
    }
    return render(request, 'export/update_address.html', context)