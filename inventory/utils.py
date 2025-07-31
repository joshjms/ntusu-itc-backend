from django.utils.crypto import get_random_string

def get_item_path(instance, filename):
    unique_identifier = get_random_string(12)
    return f'static/{unique_identifier}_{filename}'
