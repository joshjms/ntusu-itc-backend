from bs4 import BeautifulSoup
import requests
from modsoptimizer.models import CourseCode


def save_single_course_description(soup: BeautifulSoup, course: CourseCode):
    '''
    Get these information from a soup object and save them to a CourseCode instance:
    description, prerequisite, mutually_exclusive, not_available, not_available_all,
    offered_as_ue, offered_as_bde (default True for both of these, if written in the description, set to False)
    '''
    
    # get description which is the last td in the table
    description_td = soup.find_all('td')[-2]
    description = description_td.text.strip()
    course.description = description

    # get the text in the 2nd td of a tr in which the 1st td of a tr contains search_text
    def get_tr_text(soup, search_text):
        trs = soup.find_all('tr')
        for tr in trs:
            td = tr.find('td')
            if td and search_text in td.get_text():
                tds = tr.find_all('td')
                if len(tds) > 1:
                    return tds[1].get_text(strip=True)
        return None

    # extract information: mutually_exclusive, prerequisite, not_available, not_available_all
    mutually_exclusive = get_tr_text(soup, 'Mutually exclusive with:')
    prerequisite = get_tr_text(soup, 'Prerequisite:')
    not_available = get_tr_text(soup, 'Not available to Programme:')
    not_available_all = get_tr_text(soup, 'Not available to all Programme with:')
    course.prerequisite = prerequisite
    course.mutually_exclusive = mutually_exclusive
    course.not_available = not_available
    course.not_available_all = not_available_all
    
    # check if the course is not offered as UE or BDE, otherwise it's True by default
    tds = soup.find_all('td')
    for td in tds:
        if 'Not offered as Unrestricted Elective' in td.get_text():
            course.offered_as_ue = False
        if 'Not offered as Broadening and Deepening Elective' in td.get_text():
            course.offered_as_bde = False
    
    # save the changes
    course.save()

def perform_description_scraping(start_index, end_index):
    FORMDATA_ACADSEM = '2024_1'
    FORMDATA_ACAD = '2024'
    FORMDATA_SEMESTER = '1'
    
    courses = CourseCode.objects.all()
    for course in courses[start_index:end_index]:
        try:
            form_data = {
                'acadsem': FORMDATA_ACADSEM,
                'r_subj_code': course.code,
                'boption': 'Search',
                'acad': FORMDATA_ACAD,
                'semester': FORMDATA_SEMESTER,
            }
            response = requests.post(
                'https://wis.ntu.edu.sg/webexe/owa/AUS_SUBJ_CONT.main_display1',
                data=form_data
            )
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                save_single_course_description(soup, course)
            else:
                raise Exception(f'Failed to get response, status code: {response.status_code}')
        except Exception as e:
            print(e)
            print(f'Failed to scrape {course.code}')
            continue
