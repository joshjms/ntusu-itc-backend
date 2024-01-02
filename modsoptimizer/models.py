from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from modsoptimizer.utils.validation import (
    validate_index,
    validate_exam_schedule,
    validate_information,
    validate_weekly_schedule,
)


class CourseCode(models.Model):
    code = models.CharField(max_length=6, unique=True)
    name = models.CharField(max_length=100)
    academic_units = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)])
    datetime_added = models.DateTimeField(auto_now_add=True)
    exam_schedule = models.CharField(max_length=53, blank=True, validators=[validate_exam_schedule])
    common_schedule = models.CharField(max_length=192, validators=[validate_weekly_schedule])
    '''
        Let (S) denotes a 32 character string, each character represent 30 minutes interval,
        from 8am to 24pm, 16 hours in total. The character is 'X' if the interval is occupied,
        otherwise it is 'O'. The first character represents 8am to 8.30am, and so on.
        For example, 'OOOXXXXOOOOOOOOOOOOOOOOOOOOOOOOO' means that 9.30am to 11.30am is occupied.

        `exam_schedule` is stored in the following format:
        YYYY-MM-DDHH:MM-HH:MM(S)
        Example: 2023-11-0713:00-15:00OOOOOOOOOOXXXXOOOOOOOOOOOOOOOOOO
        Interpretation: Exam is on 7 Nov 2023, 1pm to 3pm.

        `common_schedule` is stored in the following format:
        (S)(S)(S)(S)(S)(S)
        Each (S) represents a day of the week, from Monday to Saturday.
        Common schedule are the occupied time slots that are common in all indexes of the course.
    '''
    # information that is common across all indexes of this course
    common_information = models.TextField(null=True, blank=True, validators=[validate_information])
    
    def serialize_info(self, info):
        single_infos = info.split('^')
        return {
            'type': single_infos[0],
            'group': single_infos[1],
            'day': single_infos[2],
            'time': single_infos[3],
            'venue': single_infos[4],
            'remark': single_infos[5],
        }

    @property
    def get_common_information(self):
        return [self.serialize_info(info_group) for info_group in self.common_information.split(';')] if \
            self.common_information else []
    
    @property
    def get_exam_schedule(self):
        if self.exam_schedule == '':
            return None
        return {
            'date': self.exam_schedule[:10],
            'time': self.exam_schedule[10:21],
            'timecode': self.exam_schedule[21:],
        }

    class Meta:
        verbose_name_plural = 'Course Codes'

    def __str__(self):
        return f'<{self.code}: {self.name}>'


class CourseIndex(models.Model):
    course = models.ForeignKey(
        CourseCode, on_delete=models.CASCADE,
        related_name='indexes')
    index = models.CharField(max_length=5, unique=True, validators=[validate_index])
    information = models.TextField(validators=[validate_information])
    schedule = models.CharField(max_length=192, validators=[validate_weekly_schedule])
    
    # only contains information that is not common across all indexes of the course that the index belongs to
    filtered_information = models.TextField(null=True, blank=True, validators=[validate_information])
    
    def serialize_info(self, info):
        single_infos = info.split('^')
        return {
            'type': single_infos[0],
            'group': single_infos[1],
            'day': single_infos[2],
            'time': single_infos[3],
            'venue': single_infos[4],
            'remark': single_infos[5],
        }

    @property
    def get_information(self):
        return [self.serialize_info(info_group) for info_group in self.information.split(';')] if \
            self.information else []
    
    @property
    def get_filtered_information(self):
        return [self.serialize_info(info_group) for info_group in self.filtered_information.split(';')] if \
            self.filtered_information else []

    class Meta:
        verbose_name_plural = 'Course Indexes'

    def __str__(self):
        return f'<Index {self.index} for course {self.course.code}>'
