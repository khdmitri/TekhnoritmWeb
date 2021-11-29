from xml.dom import minidom
from xml.etree import ElementTree
from django.utils.timezone import now

from dadata import Dadata
from django.shortcuts import get_object_or_404
from inspection.models import Protocol, DocumentSign
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

TOKEN= "92f893615d8cde3c9d4c8f6edc10314039979922"
SECRET = "19ebf698d7166d88e1a1d8465a44bab24f1bf22f"


ROLE_ID = {
    'done': 1,
    'approved': 2,
    'sign': 3,
}


class DadataClient():
    def __init__(self):
        self.dadata = Dadata(TOKEN, SECRET)

    def suggest(self, address):
        return self.dadata.suggest(name="address", query=address)

    def update_protocols(self, protocol_ids):
        protocols = list()
        for protocol_id in protocol_ids:
            protocol = get_object_or_404(Protocol, protocol_id=protocol_id)
            if protocol.ref_object.address_fias is None:
                address_fias = self.suggest(protocol.ref_object.address)
                if isinstance(address_fias, list) and len(address_fias) > 0:
                    target_object = protocol.ref_object
                    target_object.address_fias = address_fias[0]
                    target_object.save()
                    target_object.refresh_from_db()
                    protocol.refresh_from_db()
            if protocol.ref_object.address_fias is not None:
                protocols.append(protocol)
            else:
                protocol.export_error = "Адрес ФИАС не смог автоматически определиться"
                protocol.save()
        return protocols


class XMLGenerator():
    def generate(self, protocols):
        xml_document = Element('root')
        for protocol in protocols:
            try:
                protocol_node = Element('protocol')
                doc_id = SubElement(protocol_node, 'DocId')
                doc_id.text = protocol.protocol_no
                doc_creation_date = SubElement(protocol_node, 'DocCreationDate')
                doc_creation_date.text = protocol.protocol_date.strftime('%Y-%m-%d')
                doc_start_date = SubElement(protocol_node, 'DocStartDate')
                doc_start_date.text = protocol.action_date.strftime('%Y-%m-%d')
                doc_validity_date = SubElement(protocol_node, 'DocValidityDate')
                doc_validity_date.text = protocol.action_date.strftime('%Y-%m-%d')
                territory_feature = SubElement(protocol_node, 'TerritoryFeature')
                territory_feature.text = 'true'

                fias_data = protocol.ref_object.address_fias['data']

                address = SubElement(protocol_node, 'Address')
                address_details = SubElement(address, 'AddressDetails')
                id_code_oksm = SubElement(address_details, 'idCodeOksm')
                id_code_oksm.text = '643'

                unique_address = SubElement(address_details, 'UniqueAddress')
                unique_address.text = 'true'

                if fias_data.get('settlement_fias_id', None):
                    locality = fias_data['settlement_fias_id']
                else:
                    locality = fias_data['country']

                unique_address_text = SubElement(address_details, 'UniqueAddressText')
                unique_address_text.text = locality

                # if fias_data.get('region_fias_id', None):
                #     id_subject = SubElement(address_details, 'idSubject')
                #     id_subject.text = fias_data['region_fias_id']
                #

                if fias_data.get('city_fias_id', None):
                    city = SubElement(address_details, 'alienCity')
                    city.text = fias_data['city_with_type']

                if fias_data.get('area_fias_id', None):
                    district = SubElement(address_details, 'alienDistrict')
                    district.text = fias_data['area_with_type']

                locality_node = SubElement(address_details, 'alienLocality')
                locality_node.text = locality

                if fias_data.get('street', None):
                    street = SubElement(address_details, 'alienStreet')
                    street.text = fias_data['street']

                if fias_data.get('house', None):
                    house = SubElement(address_details, 'alienHouse')
                    house.text = fias_data['house']

                # if fias_data.get('flat', None):
                #     flat = SubElement(address_details, 'Flat')
                #     flat.text = fias_data['flat']

                application_date = SubElement(protocol_node, 'ApplicationDate')
                application_date.text = protocol.ref_object.ref_order.create_date.strftime('%Y-%m-%d')

                customer = SubElement(protocol_node, 'Customer')
                customer_kind_id = SubElement(customer, 'CustomerKindId')
                customer_kind_id.text = '1'

                client = protocol.ref_object.ref_order.client
                try:
                    if client.inn:
                        inn_int = int(client.inn)
                        inn_id = SubElement(customer, 'InnId')
                        inn_id.text = str(inn_int)
                except Exception as e_inn:
                    print('Cannot transform INN:', str(e_inn))

                try:
                    if client.ogrn:
                        ogrn_int = int(client.ogrn)
                        ogrn_id = SubElement(customer, 'OgrnId')
                        ogrn_id.text = str(ogrn_int)
                except Exception as e_ogrn:
                    print('Cannot transform INN:', str(e_ogrn))

                pribors = protocol.pribors.all()
                no_equipment_info = SubElement(protocol_node, 'NoEquipmentInfo')
                if pribors is not None and len(pribors) > 0:
                    no_equipment_info.text = 'false'
                    equipment = SubElement(protocol_node, 'Equipment')
                    for pribor in pribors:
                        equipment_details = SubElement(equipment, 'EquipmentDetails')
                        equipment_id = SubElement(equipment_details, 'EquipmentId')
                        equipment_id.text = str(pribor.unique_id)
                else:
                    no_equipment_info.text = 'true'

                sign_types = DocumentSign.get_sign_by_type('protocol')
                if sign_types:
                    approved_user = SubElement(protocol_node, 'ApprovedUser')
                    for detail in sign_types:
                        approved_user_details = SubElement(approved_user, 'ApprovedUserDetails')
                        id_full_name = SubElement(approved_user_details, 'idFullName')
                        id_full_name.text = str(detail.ref_person.profile.unique_id)
                        id_role_name = SubElement(approved_user_details, 'idRoleName')
                        id_role_name.text = str(ROLE_ID[detail.sign_type])

                object_info = SubElement(protocol_node, 'ObjectInfo')
                type_object_id = SubElement(object_info, 'TypeObjectId')
                type_object_id.text = '8' # окружающая среда
                full_name_object = SubElement(object_info, 'FullNameObject')
                full_name_object.text = protocol.ref_object.name

                xml_document.append(protocol_node)
                protocol.export_date = now()
                protocol.export_error = None
            except Exception as e:
                print('Error in generate:', str(e))
                protocol.export_error = str(e)
            protocol.save()

        return self.prettify(xml_document)

    @staticmethod
    def prettify(elem):
        """Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")


if __name__ == '__main__':
    dadata = DadataClient()
    print(dadata.suggest("Ульяновская область, Теренгульский район, Молвино")[0])
