from modsoptimizer.models import CourseCode, CourseCodeProgram
import re


def perform_course_additional():
    courses = CourseCode.objects.all()
    for course in courses:
        code = course.code
        
        # refer to models.py for explanation
        # in CourseCode model, for 'level' and 'program_code'
        
        # program code
        match = re.match(r'([A-Za-z]+)([0-9]+)', code)
        program_code = ''
        if match:
            program_code = match.group(1)
        course.program_code = program_code

        # level
        numeric_part = match.group(2) if match else ''
        level = 10
        if numeric_part and numeric_part.isdigit() and len(numeric_part) == 4:
            first_digit = int(numeric_part[0])
            level = first_digit if 1 <= first_digit <= 5 else 10
        course.level = level

        course.save()
        
    # populate course code program
    CourseCodeProgram.objects.all().delete()
    program_codes = CourseCode.objects.values_list('program_code', flat=True).distinct()
    for program_code in program_codes:
        CourseCodeProgram.objects.create(program_code=program_code)
