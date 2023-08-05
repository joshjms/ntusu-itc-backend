from bs4 import BeautifulSoup
from django.db.utils import IntegrityError
from urllib import request
import re
from indexswapper.models import CourseIndex


# latest link: AY 2023-2024 Semester 1
# https://wish.wis.ntu.edu.sg/webexe/owa/AUS_SCHEDULE.main_display1?acadsem=2023;1&staff_access=true&r_search_type=F&boption=Search&r_subj_code=
def get_url(acadyear, acadsem):
    return f"https://wish.wis.ntu.edu.sg/webexe/owa/AUS_SCHEDULE.main_display1?acadsem={acadyear};{acadsem}&staff_access=true&r_search_type=F&boption=Search&r_subj_code="


'''
    Web scraper that scrapes the NTU website for the module information.
    Author: Clayton Fernalo
'''


def populate_modules(max_indexes=99999, url='some_url'):

    index_counter = 0
    duplicate_count = 0

    with request.urlopen(url) as fp:
        # Parsing the html from the URL into a nested data structure
        soup = BeautifulSoup(fp, "lxml")

        course_list = soup.find_all('table')
        for header, body in zip(course_list[0::2], course_list[1::2]):

            # Obtaining information from the header part (which consists of course code, name, pre-requisites, etc.)
            header_content = header.find_all('td')

            code = header_content[0].get_text()

            name = re.findall(".*(?<![*~#^])", header_content[1].get_text())[0]

            raw_au = re.findall(".(?=\.0 AU)", header_content[2].get_text())[0]
            academic_units = 0
            try:  # .0 AU -> E1102L (buggy there)
                academic_units = int(raw_au) if raw_au else 0
            except:
                pass

            # raw data containing the index table without the header
            index_content = body.find_all('tr')[1:]
            index_information = []  # list containing a tuple of TYPE, GROUP, DAY, TIME, LOC, REMARKS
            index = ''  # previous index

            for row in index_content:
                if (row.td.get_text()):  # Row that contains an index a.k.a. new index
                    if (index):
                        # not the first index a.k.a. prev_index is still empty so no creating a new instance
                        # creates a new instance on the database
                        # creates information string
                        information = ''

                        for i in range(0, len(index_information)):
                            for j in range(0, 6):
                                information += (index_information[i]
                                                [j] + '^' if j < 5 else '')
                            information += ';' if i < (
                                len(index_information)-1) else ''

                        try:
                            CourseIndex.objects.create(
                                code=code,
                                name=name,
                                academic_units=academic_units,
                                index=index,
                                information=information
                            )
                        except IntegrityError:
                            duplicate_count += 1

                        index_counter += 1
                        if index_counter >= max_indexes:
                            return

                    # Resets the value
                    index = row.td.get_text()
                    index_information = []  # Tuples for a certain index

                # Holds the tuple temporarily before being inserted into index_information
                column_information = []
                for column in row.find_all('td')[1:]:
                    column_information.append(column.get_text())
                    index_information.append(column_information)

                if (row == index_content[-1]):
                    # Last row so need to create new instance here
                    information = ''

                    for i in range(0, len(index_information)):
                        for j in range(0, 6):
                            information += (index_information[i]
                                            [j] + '^' if j < 5 else '')
                        information += ';' if i < (
                            len(index_information)-1) else ''

                    try:
                        CourseIndex.objects.create(
                            code=code,
                            name=name,
                            academic_units=academic_units,
                            index=index,
                            information=information
                        )
                    except IntegrityError:
                        duplicate_count += 1

                    index_counter += 1
                    if index_counter >= max_indexes:
                        return

    # print(duplicate_count)
    return
