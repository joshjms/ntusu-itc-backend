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
    
    description = models.TextField(null=True, blank=True)
    prerequisite = models.CharField(max_length=300, null=True, blank=True)
    mutually_exclusive = models.CharField(max_length=300, null=True, blank=True)
    not_available = models.CharField(max_length=300, null=True, blank=True)
    not_available_all = models.CharField(max_length=300, null=True, blank=True)
    offered_as_ue = models.BooleanField(default=True)
    offered_as_bde = models.BooleanField(default=True)
    grade_type = models.CharField(max_length=300, null=True, blank=True)
    not_offered_as_core_to = models.CharField(max_length=300, null=True, blank=True)
    not_offered_as_pe_to = models.CharField(max_length=300, null=True, blank=True)
    not_offered_as_bde_ue_to = models.CharField(max_length=300, null=True, blank=True)
    department_maintaining = models.CharField(max_length=50, null=True, blank=True)
    program_list = models.CharField(max_length=1000, null=True, blank=True)
    
    # level of the course, determined by the first non-letter character in the course code
    # currently only store level 1 to 5, the rest will be stored as 10
    # if the number after the letters are less than 4 digits, it will be stored as 10
    # example: lv1: MH1101, SC1003; lv3: MH3700, E3102L
    # level 10: AAA28R, AAI28C, AGE18A, ES9003
    level = models.CharField(max_length=2, null=True, blank=True)
    # program of the course (characters up to and excluding the first non-letter character)
    # example: MH3701 -> program_code = 'MH'
    # program_code = 'E'
    # AAA28R -> program_code = 'AAA'
    program_code = models.CharField(max_length=3, null=True, blank=True)
    # these 'level' and 'program_code' are programatically populated
    # from 'scrape_course_additional' api endpoint
    
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
    
    '''
    Per June 2024, all course codes in db have been asserted to have length of 6.
    Level is determined by the third character.
    For example, 'MH1100' is a level 1 course, 'MH3700' is a level 3 course.
    Currently, we only classify level 1 to 5 course,
    the rest will be integer 10 which are classified as 'others'.
    '''
    @property
    def get_level(self):
        digit = self.code[2]
        if digit.isdigit() and int(digit) in range(1, 6):
            return int(digit)
        return 10

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


class CourseProgram(models.Model):
    name = models.CharField(max_length=300, unique=True)
    value = models.CharField(max_length=300, unique=True)
    datetime_added = models.DateTimeField(auto_now_add=True)
    courses = models.ManyToManyField(CourseCode, related_name='programs')
    year = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True)
    
    def __str__(self):
        return f'<CourseProgram ID #{self.id}: {self.name}>'
    
    class Meta:
        verbose_name_plural = 'Course Programs'
