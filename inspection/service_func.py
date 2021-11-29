from .models import ProtocolPoints
from math import floor


def floatFloor(number, base):
    try:
        res = floor(number * pow(10, base)) / pow(10, base)
    except Exception:
        res = 0
    return res


def is_float(value):
    try:
        float(value)
        return True
    except:
        return False


SERVICE_ROOM_POINTS = {
    1: {'place': 'Аппаратная',
        'value': '<0.3',
        'pdu': '10',
        'unit': 'мкВт/см2',
        'distance': '0.3',
        'high': '1.7'},
    2: {'place': 'Аппаратная',
        'value': '<0.3',
        'pdu': '10',
        'unit': 'мкВт/см2',
        'distance': '0.3',
        'high': '1',
        },
    3: {'place': 'Аппаратная',
        'value': '<0.3',
        'pdu': '10',
        'unit': 'мкВт/см2',
        'distance': '0.3',
        'high': '0.5',
        }
}


def add_service_points(protocol):
    points = ProtocolPoints.get_points_by_protocol(protocol)
    # Clear point no
    for point in points:
        if point.no:
            point.no += len(SERVICE_ROOM_POINTS)
            point.save()

    for key in SERVICE_ROOM_POINTS:
        item = SERVICE_ROOM_POINTS[key]
        ProtocolPoints.objects.create(ref_protocol=protocol,
                                      no=key,
                                      place=item['place'],
                                      value=item['value'],
                                      pdu=item['pdu'],
                                      unit=item['unit'],
                                      distance=item['distance'],
                                      high=item['high'])
    return True
