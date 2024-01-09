from collections import OrderedDict
from modsoptimizer.models import CourseCode, CourseIndex


def merge_mask(mask1: str, mask2: str, common_schedule_mask = None):
    '''
    Merge two masks together, return None if there is a clash.
    '''

    if len(mask1) != len(mask2):
        raise ValueError("The lengths of the masks are not equal")

    mask = ""
    for i in range(len(mask1)):
        if common_schedule_mask is not None and common_schedule_mask[i] == "X":
            mask += "X"
        elif mask1[i] == "X" and mask2[i] == "X":
            return None
        elif mask1[i] == "O" and mask2[i] == "O":
            mask += "O"
        else:
            mask += "X"

    return mask

def backtrack(mask: str, course_schedule: dict, common_schedule: dict):
    '''
    Backtrack to fill in the mask with the course schedule.
    '''

    curr_course, course_index_list = course_schedule.popitem()
    common_schedule_mask = common_schedule[curr_course]

    for index in course_index_list:    
        # check if adding the index is possible
        new_mask = merge_mask(mask, index.schedule, common_schedule_mask)
        if new_mask is None:
            continue
        
        # if there is no more course schedule, return the result
        if len(course_schedule) == 0:
            # add back the course schedule that is popped out
            course_schedule[curr_course] = course_index_list 
            return {
                "data": [
                    {
                        "code": curr_course,
                        "index": index.index,
                    }
                ],
                "error": "",
            }
        
        # if there is still course schedule, backtrack
        result = backtrack(new_mask, course_schedule, common_schedule)

        # if there is no error, return the result
        if result["error"] == "":
            # add back the course schedule that is popped out
            course_schedule[curr_course] = course_index_list 

            result["data"].append({
                "code": curr_course,
                "index": index.index,
            })
            return result
    
    # add back the course schedule that is popped out
    course_schedule[curr_course] = course_index_list 

    return {
        "data": [],
        "error": f"Not possible to add course schedule of Course Code {curr_course}"
    }
    

def optimize_index(optimizer_input_data: OrderedDict):
    '''
    Optimize fitting in the index of the course code.
    If possible, return a list of the possible indexes.
    If not possible, return error of the reason.
    Example Input:
    {
        "courses": [
            {
                "code": "MH1810",
                "include": []
                "exclude": []
            }
        ],
        "occupied": ""
    }

    Example Output:
    {
        "data": [
            {
                "code": "MH1810",
                "index": "50001",
            }
        ]
        "error": "",
    }
    '''

    # start with the occupied mask
    if "occupied" not in optimizer_input_data:
        mask = "O" * 192
    else:
        mask = optimizer_input_data["occupied"]

    # get the course schedule, exam schedule and common schedule
    exam_schedule = {}
    common_schedule = {}
    course_schedule = {}
    for course in optimizer_input_data["courses"]:
        course_code = course["code"]
        course_info = CourseCode.objects.get(code=course_code) # get the course info
        course_indexes = course_info.indexes.all() # get all the index of the course
        
        if "include" in course and len(course["include"]) != 0:
            # if the include list is not empty, filter the course_indexes
            course_indexes = course_indexes.filter(index__in=course["include"])
        elif "exclude" in course and len(course["exclude"]) != 0:
            # if the exclude list is not empty, filter the course_indexes
            course_indexes = course_indexes.exclude(index__in=course["exclude"])
        
        exam_schedule[course_code] = course_info.get_exam_schedule
        common_schedule[course_code] = course_info.common_schedule
        course_schedule[course_code] = course_indexes 
    

    # check exam schedule clash
    exam_masks = {}
    for course_code in exam_schedule:
        if exam_schedule[course_code] is None:
            continue
        
        exam_date = exam_schedule[course_code]["date"]
        exam_mask = exam_schedule[course_code]["timecode"]

        if exam_date not in exam_masks:
            exam_masks[exam_date] = exam_mask
            continue

        new_mask = merge_mask(exam_masks[exam_date], exam_mask)
        if new_mask is None:
            return {
                "data": [],
                "error": f"Not possible to add exam schedule of Course Code {course_code}"
            }
        exam_masks[exam_date] = new_mask

    
    # fill in the mask with the common schedule
    for course_code in common_schedule:
        if common_schedule[course_code] is None:
            continue

        mask = merge_mask(mask, common_schedule[course_code])
        if mask is None:
            return {
            "data": [],
            "error": f"Not possible to add common schedule of Course Code {course_code}"
        }
        
    
    # backtrack to fill in the mask with the course schedule
    return backtrack(mask, course_schedule, common_schedule)