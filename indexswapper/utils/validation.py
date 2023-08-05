from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.db.models import Model
from rest_framework.exceptions import APIException


class ConvertibleListIndexValidator(BaseValidator):
    def __init__(self, model: Model, current_course_code: str):
        self.model = model
        self.course_code = current_course_code

    def __call__(self, value: str):
        try:
            evaluated_value = eval(value)
            if not isinstance(evaluated_value, list):
                raise ValidationError('Value is not convertible to a list.')
            if len(evaluated_value) == 0:
                raise ValidationError('List cannot be empty.')
            for index in evaluated_value:
                if not self.model.objects.filter(index=index).exists():
                    raise ValidationError(f'Index {index} does not exist.')
                instance = self.model.objects.get(index=index)
                if self.course_code != instance.code:
                    raise ValidationError(
                        f'Index {index} ({instance.code}) is not from the same course code with current index (code needed: {self.course_code})')
        except (NameError, SyntaxError):
            raise ValidationError('Value is not convertible to a list.')


class ConflictValidationError(APIException):
    status_code = 409
    default_detail = 'Conflict.'

    def __init__(self, detail=None, code=None):
        if detail is not None:
            self.detail = {'detail': str(detail)}
        else:
            self.detail = {'detail': str(self.default_detail)}
        self.code = code
