from bs4 import BeautifulSoup
from django.db.utils import IntegrityError
import requests

from modsoptimizer.models import CourseCode, CourseProgram
from modsoptimizer.utils.scraping_files.program_constant import html_content


def save_single_program_content(soup: BeautifulSoup, program: CourseProgram):
    tables = soup.find_all('table')
    for table in tables:
        first_tr = table.find('tr')
        if first_tr:
            first_td = first_tr.find('td')
            if first_td:
                code = first_td.get_text(strip=True)
                course_code_instance = CourseCode.objects.filter(code=code).first()
                if not course_code_instance:
                    print(f'Course with code {code} not found')
                    continue
                program.courses.add(course_code_instance)
                programs_list = course_code_instance.program_list.split(', ') \
                    if course_code_instance.program_list else []
                programs_list.append(program.name)
                unique_programs_list = list(set(programs_list))
                course_code_instance.program_list = ', '.join(unique_programs_list)
                course_code_instance.save()

def perform_program_scraping(start_index, end_index):
    # populate course program
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        options = soup.find('select', {'name': 'r_course_yr'}).find_all('option')
        programs = []
        for option in options:
            text = option.get_text(strip=True)
            value = option.get('value')
            if value == '': # skip the first option
                continue
            year = None
            try:
                year = int(value.split(';')[2])
            except ValueError:
                pass
            programs.append({
                'name': text,
                'value': value,
                'year': year,
            })
            
        for program in programs[start_index:end_index]:
            try:
                CourseProgram.objects.create(
                    name=program['name'],
                    value=program['value'],
                    year=program['year'],
                )
            except IntegrityError:
                pass
    except Exception as e:
        print(e)
        print('Failed to populate course program')
        return
        
    # add the courses for each program in many to many field
    ENDPOINT = 'https://wis.ntu.edu.sg/webexe/owa/AUS_SUBJ_CONT.main_display1'
    FORMDATA_ACADSEM = '2024_1'
    FORMDATA_ACAD = '2024'
    FORMDATA_SEMESTER = '1'
    
    programs = CourseProgram.objects.all()
    for program in programs[start_index:end_index]:
        try:
            form_data = {
                'acadsem': FORMDATA_ACADSEM,
                'r_course_yr': program.value,
                'r_subj_code': '',
                'boption': 'CLoad',
                'acad': FORMDATA_ACAD,
                'semester': FORMDATA_SEMESTER,
            }
            response = requests.post(
                ENDPOINT,
                data=form_data
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                save_single_program_content(soup, program)
            else:
                raise Exception(f'Failed to get response, status code: {response.status_code}')
        except Exception as e:
            print(e)
            print(f'Failed to scrape program {program.name}')
            continue
