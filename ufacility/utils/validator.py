from django.core.exceptions import ValidationError
import re


'''
    Check if a value is a valid singapore phone number.
    Singapore phone number should start with 6 / 8 / 9, followed with 7 digits.
'''
def validate_singapore_phone_number(value):
    pattern = re.compile(r'^[689]\d{7}$')
    if not pattern.match(value):
        raise ValidationError('Invalid Singapore phone number.')
