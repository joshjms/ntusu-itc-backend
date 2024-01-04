'''
    The script below is to be executed after course_scraper and exam_scraper.
    Information is before stored in each CourseIndex instances only.
    We want to move information that is common across all indexes of a course to the
    'common_information' field of CourseCode instance.
    The remaining information will be stored in the CourseIndex instance in
    'filtered_information' field.
    The original 'information' field of CourseIndex instance is unchanged.
'''
from collections import Counter
from modsoptimizer.models import CourseCode


def perform_info_update():
    course_codes = CourseCode.objects.all()
    for course_code in course_codes:
        course_indexes = course_code.indexes.all()

        # get `common_information_list`, a list of information strings that are common across all indexes of this course
        information_dict = Counter()
        for index_instance in course_indexes:
            information_dict.update(index_instance.information.split(';'))
        common_information_list = [info for info, count in information_dict.items() if count == course_indexes.count()]

        # update `common_information` field of course_code
        course_code.common_information = ';'.join(common_information_list)
        course_code.save()

        # update `filtered_information` field of course_indexes
        for index_instance in course_indexes:
            index_instance.filtered_information = ';'.join(set(index_instance.information.split(';')) - set(common_information_list))
            index_instance.save()
