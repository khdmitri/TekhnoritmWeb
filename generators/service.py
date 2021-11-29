from .models import Generator


def get_new_value(use_area):
    if use_area:
        new_obj = Generator.set_new(use_area)
        return str(new_obj)
    else:
        return ''
