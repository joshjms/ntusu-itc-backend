from rest_framework.test import APITestCase
import os
from modsoptimizer.models import CourseCode, CourseIndex
from modsoptimizer.utils.course_scraper import get_raw_data, process_data, save_course_data
from modsoptimizer.utils.exam_scraper import get_soup_from_html_file


class TestCourseScraper(APITestCase):
    '''
    Given soup of courses page, test these functions from `test_course_scraper`:
    - get_raw_data
    - process_data
    - save_course_data
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        FILE_PATH = os.path.join('modsoptimizer', 'utils', 'scraping_files', 'course_schedule.html')
        self.soup = get_soup_from_html_file(FILE_PATH)

    def get_schedule_str(self, *args):
        # return a string of 'O' of length 192 (32 * 6) with 'X' on the given args (1 index)
        schedule_list = ['O'] * 192
        for arg in args:
            schedule_list[arg - 1] = 'X'
        return ''.join(schedule_list)

    def test_course_scraper_1(self):
        raw_data = get_raw_data(self.soup, 0, 0)
        self.assertEqual(raw_data,
        [
            (
                {
                    "course_code": "AAA08B",
                    "course_name": "FASHION & DESIGN: WEARABLE ART AS A SECOND SKIN",
                    "academic_units": 3,
                },
                [
                    {
                        "index": "39619",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "LE",
                                "day": "THU",
                                "time": "1330-1620",
                                "venue": "NIE7-02-07",
                                "remark": "",
                            }
                        ],
                    }
                ],
            )
        ])
        processed_data = process_data(raw_data)
        self.assertEqual(processed_data,
        [
            {
                "course_code": "AAA08B",
                "course_name": "FASHION & DESIGN: WEARABLE ART AS A SECOND SKIN",
                "academic_units": 3,
                "indexes": [
                    {
                        "index": "39619",
                        "schedule": self.get_schedule_str(108, 109, 110, 111, 112, 113),
                        "information": "LEC/STUDIO^LE^THU^1330-1620^NIE7-02-07^",
                    }
                ],
                "common_schedule": self.get_schedule_str(108, 109, 110, 111, 112, 113),
            }
        ])
        save_course_data(processed_data)
        course_code = CourseCode.objects.get(code='AAA08B')
        self.assertEqual(course_code.name, 'FASHION & DESIGN: WEARABLE ART AS A SECOND SKIN')
        self.assertEqual(course_code.academic_units, 3)
        self.assertEqual(course_code.common_schedule, self.get_schedule_str(108, 109, 110, 111, 112, 113))
        course_index = CourseIndex.objects.get(index='39619')
        self.assertEqual(course_index.course, course_code)
        self.assertEqual(course_index.schedule, self.get_schedule_str(108, 109, 110, 111, 112, 113))
        self.assertEqual(course_index.information, "LEC/STUDIO^LE^THU^1330-1620^NIE7-02-07^")
        self.assertEqual(course_index.get_information, [
            {
                "type": "LEC/STUDIO",
                "group": "LE",
                "day": "THU",
                "time": "1330-1620",
                "venue": "NIE7-02-07",
                "remark": "",
            }
        ])

    def test_course_scraper_2(self):
        raw_data = get_raw_data(self.soup, 4, 4)
        self.assertEqual(raw_data,
        [
            (

                {
                    "course_code": "AAA18E",
                    "course_name": "DRAWING",
                    "academic_units": 3
                },
                [
                    {
                        "index": "39621",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "LG1",
                                "day": "TUE",
                                "time": "1130-1420",
                                "venue": "NIE3-B1-10",
                                "remark": "",
                            }
                        ],
                    },
                    {
                        "index": "39622",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "LG2",
                                "day": "WED",
                                "time": "1130-1420",
                                "venue": "NIE-TR319",
                                "remark": "Teaching Wk1-11,13",
                            }
                        ],
                    },
                    {
                        "index": "39623",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "LG3",
                                "day": "WED",
                                "time": "1430-1720",
                                "venue": "NIE-TR319",
                                "remark": "Teaching Wk1-11,13",
                            }
                        ],
                    },
                ],
            )
        ])
        processed_data = process_data(raw_data)
        self.assertEqual(processed_data,
        [
            {
                "course_code": "AAA18E",
                "course_name": "DRAWING",
                "academic_units": 3,
                "indexes": [
                    {
                        "index": "39621",
                        "schedule": self.get_schedule_str(40, 41, 42, 43, 44, 45),
                        "information": "LEC/STUDIO^LG1^TUE^1130-1420^NIE3-B1-10^",
                    },
                    {
                        "index": "39622",
                        "schedule": self.get_schedule_str(72, 73, 74, 75, 76, 77),
                        "information": "LEC/STUDIO^LG2^WED^1130-1420^NIE-TR319^Teaching Wk1-11,13",
                    },
                    {
                        "index": "39623",
                        "schedule": self.get_schedule_str(78, 79, 80, 81, 82, 83),
                        "information": "LEC/STUDIO^LG3^WED^1430-1720^NIE-TR319^Teaching Wk1-11,13",
                    },
                ],
                "common_schedule": self.get_schedule_str(),
            }
        ])
        save_course_data(processed_data)
        course_code = CourseCode.objects.get(code='AAA18E')
        self.assertEqual(course_code.name, 'DRAWING')
        self.assertEqual(course_code.academic_units, 3)
        self.assertEqual(course_code.common_schedule, self.get_schedule_str())
        course_index_1 = CourseIndex.objects.get(index='39621')
        self.assertEqual(course_index_1.course, course_code)
        self.assertEqual(course_index_1.schedule, self.get_schedule_str(40, 41, 42, 43, 44, 45))
        self.assertEqual(course_index_1.information, "LEC/STUDIO^LG1^TUE^1130-1420^NIE3-B1-10^")
        self.assertEqual(course_index_1.get_information, [
            {
                "type": "LEC/STUDIO",
                "group": "LG1",
                "day": "TUE",
                "time": "1130-1420",
                "venue": "NIE3-B1-10",
                "remark": "",
            }
        ])
        course_index_2 = CourseIndex.objects.get(index='39622')
        self.assertEqual(course_index_2.course, course_code)
        self.assertEqual(course_index_2.schedule, self.get_schedule_str(72, 73, 74, 75, 76, 77))
        self.assertEqual(course_index_2.information, "LEC/STUDIO^LG2^WED^1130-1420^NIE-TR319^Teaching Wk1-11,13")
        self.assertEqual(course_index_2.get_information, [
            {
                "type": "LEC/STUDIO",
                "group": "LG2",
                "day": "WED",
                "time": "1130-1420",
                "venue": "NIE-TR319",
                "remark": "Teaching Wk1-11,13",
            }
        ])
        course_index_3 = CourseIndex.objects.get(index='39623')
        self.assertEqual(course_index_3.course, course_code)
        self.assertEqual(course_index_3.schedule, self.get_schedule_str(78, 79, 80, 81, 82, 83))
        self.assertEqual(course_index_3.information, "LEC/STUDIO^LG3^WED^1430-1720^NIE-TR319^Teaching Wk1-11,13")
        self.assertEqual(course_index_3.get_information, [
            {
                "type": "LEC/STUDIO",
                "group": "LG3",
                "day": "WED",
                "time": "1430-1720",
                "venue": "NIE-TR319",
                "remark": "Teaching Wk1-11,13",
            }
        ])

    def test_course_scraper_3(self):
        raw_data = get_raw_data(self.soup, 17, 17)
        self.assertEqual(raw_data,
        [
            (
                {
                    "course_code": "AAE18B",
                    "course_name": "LANGUAGE IN CONTEXT",
                    "academic_units": 3,
                },
                [
                    {
                        "index": "39291",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "LE",
                                "day": "THU",
                                "time": "1130-1220",
                                "venue": "NIE3-TR318",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "T",
                                "day": "WED",
                                "time": "1430-1620",
                                "venue": "NIE3-TR318",
                                "remark": "",
                            },
                        ],
                    }
                ],
            )
        ])
        processed_data = process_data(raw_data)
        self.assertEqual(processed_data,
        [
            {
                "course_code": "AAE18B",
                "course_name": "LANGUAGE IN CONTEXT",
                "academic_units": 3,
                "indexes": [
                    {
                        "index": "39291",
                        "schedule": self.get_schedule_str(78, 79, 80, 81, 104, 105),
                        "information": "LEC/STUDIO^LE^THU^1130-1220^NIE3-TR318^;TUT^T^WED^1430-1620^NIE3-TR318^",
                    }
                ],
                "common_schedule": self.get_schedule_str(78, 79, 80, 81, 104, 105),
            }
        ])
        save_course_data(processed_data)
        course_code = CourseCode.objects.get(code='AAE18B')
        self.assertEqual(course_code.name, 'LANGUAGE IN CONTEXT')
        self.assertEqual(course_code.academic_units, 3)
        self.assertEqual(course_code.common_schedule, self.get_schedule_str(78, 79, 80, 81, 104, 105))
        course_index = CourseIndex.objects.get(index='39291')
        self.assertEqual(course_index.course, course_code)
        self.assertEqual(course_index.schedule, self.get_schedule_str(78, 79, 80, 81, 104, 105))
        self.assertEqual(course_index.information, "LEC/STUDIO^LE^THU^1130-1220^NIE3-TR318^;TUT^T^WED^1430-1620^NIE3-TR318^")
        self.assertEqual(course_index.get_information, [
            {
                "type": "LEC/STUDIO",
                "group": "LE",
                "day": "THU",
                "time": "1130-1220",
                "venue": "NIE3-TR318",
                "remark": "",
            },
            {
                "type": "TUT",
                "group": "T",
                "day": "WED",
                "time": "1430-1620",
                "venue": "NIE3-TR318",
                "remark": "",
            },
        ])

    def test_course_scraper_4(self):
        raw_data = get_raw_data(self.soup, 47, 47)
        self.assertEqual(raw_data,
        [
            (
                {
                    "course_code": "AB1403",
                    "course_name": "INTERMEDIATE EXCEL",
                    "academic_units": 1,
                },
                [
                    {
                        "index": "00535",
                        "info": [
                            {
                                "type": "\xa0",
                                "group": "1",
                                "day": "\xa0",
                                "time": "\xa0",
                                "venue": "\xa0",
                                "remark": "  Online Course ",
                            }
                        ],
                    }
                ],
            )
        ])
        processed_data = process_data(raw_data)
        self.assertEqual(processed_data,
        [
            {
                "course_code": "AB1403",
                "course_name": "INTERMEDIATE EXCEL",
                "academic_units": 1,
                "indexes": [
                    {
                        "index": "00535",
                        "schedule": self.get_schedule_str(),
                        "information": "\xa0^1^\xa0^\xa0^\xa0^  Online Course ",
                    }
                ],
                "common_schedule": self.get_schedule_str(),
            }
        ])
        save_course_data(processed_data)
        course_code = CourseCode.objects.get(code='AB1403')
        self.assertEqual(course_code.name, 'INTERMEDIATE EXCEL')
        self.assertEqual(course_code.academic_units, 1)
        self.assertEqual(course_code.common_schedule, self.get_schedule_str())
        course_index = CourseIndex.objects.get(index='00535')
        self.assertEqual(course_index.course, course_code)
        self.assertEqual(course_index.schedule, self.get_schedule_str())
        self.assertEqual(course_index.information, "\xa0^1^\xa0^\xa0^\xa0^  Online Course ")
        self.assertEqual(course_index.get_information, [
            {
                "type": "\xa0",
                "group": "1",
                "day": "\xa0",
                "time": "\xa0",
                "venue": "\xa0",
                "remark": "  Online Course ",
            }
        ])

    def test_course_scraper_5(self):
        raw_data = get_raw_data(self.soup, 48, 48)
        self.assertEqual(raw_data,
        [
            (
                {
                    "course_code": "AB1501",
                    "course_name": "MARKETING",
                    "academic_units": 3,
                },
                [
                    {
                        "index": "00680",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "1",
                                "day": "MON",
                                "time": "0830-1020",
                                "venue": "TR+30",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00681",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "2",
                                "day": "MON",
                                "time": "1030-1220",
                                "venue": "TR+30",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00682",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "3",
                                "day": "FRI",
                                "time": "0830-1020",
                                "venue": "TR+30",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00683",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "4",
                                "day": "TUE",
                                "time": "0830-1020",
                                "venue": "TR+108",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00684",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "5",
                                "day": "TUE",
                                "time": "0830-1020",
                                "venue": "TR+30",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00685",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "6",
                                "day": "TUE",
                                "time": "1030-1220",
                                "venue": "LHS-TR+55",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00686",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "7",
                                "day": "TUE",
                                "time": "1030-1220",
                                "venue": "TR+30",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00687",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "8",
                                "day": "TUE",
                                "time": "1030-1220",
                                "venue": "TR+92",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00688",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "9",
                                "day": "TUE",
                                "time": "1330-1520",
                                "venue": "TR+92",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00689",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "10",
                                "day": "TUE",
                                "time": "1330-1520",
                                "venue": "TR+30",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00690",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "11",
                                "day": "TUE",
                                "time": "1330-1520",
                                "venue": "LHS-TR+42",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00691",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "12",
                                "day": "TUE",
                                "time": "1530-1720",
                                "venue": "LHS-TR+42",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00692",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "13",
                                "day": "TUE",
                                "time": "1530-1720",
                                "venue": "TR+30",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00693",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "14",
                                "day": "TUE",
                                "time": "1530-1720",
                                "venue": "TR+92",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00694",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "15",
                                "day": "MON",
                                "time": "1330-1520",
                                "venue": "TR+30",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00695",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "16",
                                "day": "FRI",
                                "time": "1030-1220",
                                "venue": "TR+108",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00696",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "17",
                                "day": "FRI",
                                "time": "0830-1020",
                                "venue": "TR+31",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00697",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "18",
                                "day": "MON",
                                "time": "1530-1720",
                                "venue": "TR+30",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00698",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "19",
                                "day": "FRI",
                                "time": "1030-1220",
                                "venue": "TR+30",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00699",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "20",
                                "day": "FRI",
                                "time": "1330-1520",
                                "venue": "TR+108",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00700",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "21",
                                "day": "FRI",
                                "time": "1330-1520",
                                "venue": "TR+30",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00701",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "22",
                                "day": "FRI",
                                "time": "1530-1720",
                                "venue": "TR+108",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00702",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "23",
                                "day": "FRI",
                                "time": "1530-1720",
                                "venue": "TR+30",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00703",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "24",
                                "day": "FRI",
                                "time": "1530-1720",
                                "venue": "TR+107",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                    {
                        "index": "00704",
                        "info": [
                            {
                                "type": "LEC/STUDIO",
                                "group": "1",
                                "day": "WED",
                                "time": "0930-1020",
                                "venue": "ONLINE",
                                "remark": "",
                            },
                            {
                                "type": "TUT",
                                "group": "25",
                                "day": "FRI",
                                "time": "1030-1220",
                                "venue": "TR+31",
                                "remark": "Teaching Wk2-13",
                            },
                        ],
                    },
                ],
            )
        ])
        processed_data = process_data(raw_data)
        self.assertEqual(processed_data,
        [
            {
                "course_code": "AB1501",
                "course_name": "MARKETING",
                "academic_units": 3,
                "indexes": [
                    {
                        "index": "00680",
                        "schedule": self.get_schedule_str(68, 69, 2, 3, 4, 5),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^1^MON^0830-1020^TR+30^Teaching Wk2-13",
                    },
                    {
                        "index": "00681",
                        "schedule": self.get_schedule_str(68, 69, 6, 7, 8, 9),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^2^MON^1030-1220^TR+30^Teaching Wk2-13",
                    },
                    {
                        "index": "00682",
                        "schedule": self.get_schedule_str(68, 69, 130, 131, 132, 133),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^3^FRI^0830-1020^TR+30^Teaching Wk2-13",
                    },
                    {
                        "index": "00683",
                        "schedule": self.get_schedule_str(68, 69, 34, 35, 36, 37),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^4^TUE^0830-1020^TR+108^Teaching Wk2-13",
                    },
                    {
                        "index": "00684",
                        "schedule": self.get_schedule_str(68, 69, 34, 35, 36, 37),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^5^TUE^0830-1020^TR+30^Teaching Wk2-13",
                    },
                    {
                        "index": "00685",
                        "schedule": self.get_schedule_str(68, 69, 38, 39, 40, 41),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^6^TUE^1030-1220^LHS-TR+55^Teaching Wk2-13",
                    },
                    {
                        "index": "00686",
                        "schedule": self.get_schedule_str(68, 69, 38, 39, 40, 41),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^7^TUE^1030-1220^TR+30^Teaching Wk2-13",
                    },
                    {
                        "index": "00687",
                        "schedule": self.get_schedule_str(68, 69, 38, 39, 40, 41),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^8^TUE^1030-1220^TR+92^Teaching Wk2-13",
                    },
                    {
                        "index": "00688",
                        "schedule": self.get_schedule_str(68, 69, 44, 45, 46, 47),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^9^TUE^1330-1520^TR+92^Teaching Wk2-13",
                    },
                    {
                        "index": "00689",
                        "schedule": self.get_schedule_str(68, 69, 44, 45, 46, 47),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^10^TUE^1330-1520^TR+30^Teaching Wk2-13",
                    },
                    {
                        "index": "00690",
                        "schedule": self.get_schedule_str(68, 69, 44, 45, 46, 47),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^11^TUE^1330-1520^LHS-TR+42^Teaching Wk2-13",
                    },
                    {
                        "index": "00691",
                        "schedule": self.get_schedule_str(68, 69, 48, 49, 50, 51),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^12^TUE^1530-1720^LHS-TR+42^Teaching Wk2-13",
                    },
                    {
                        "index": "00692",
                        "schedule": self.get_schedule_str(68, 69, 48, 49, 50, 51),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^13^TUE^1530-1720^TR+30^Teaching Wk2-13",
                    },
                    {
                        "index": "00693",
                        "schedule": self.get_schedule_str(68, 69, 48, 49, 50, 51),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^14^TUE^1530-1720^TR+92^Teaching Wk2-13",
                    },
                    {
                        "index": "00694",
                        "schedule": self.get_schedule_str(68, 69, 12, 13, 14, 15),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^15^MON^1330-1520^TR+30^Teaching Wk2-13",
                    },
                    {
                        "index": "00695",
                        "schedule": self.get_schedule_str(68, 69, 134, 135, 136, 137),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^16^FRI^1030-1220^TR+108^Teaching Wk2-13",
                    },
                    {
                        "index": "00696",
                        "schedule": self.get_schedule_str(68, 69, 130, 131, 132, 133),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^17^FRI^0830-1020^TR+31^Teaching Wk2-13",
                    },
                    {
                        "index": "00697",
                        "schedule": self.get_schedule_str(68, 69, 16, 17, 18, 19),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^18^MON^1530-1720^TR+30^Teaching Wk2-13",
                    },
                    {
                        "index": "00698",
                        "schedule": self.get_schedule_str(68, 69, 134, 135, 136, 137),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^19^FRI^1030-1220^TR+30^Teaching Wk2-13",
                    },
                    {
                        "index": "00699",
                        "schedule": self.get_schedule_str(68, 69, 140, 141, 142, 143),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^20^FRI^1330-1520^TR+108^Teaching Wk2-13",
                    },
                    {
                        "index": "00700",
                        "schedule": self.get_schedule_str(68, 69, 140, 141, 142, 143),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^21^FRI^1330-1520^TR+30^Teaching Wk2-13",
                    },
                    {
                        "index": "00701",
                        "schedule": self.get_schedule_str(68, 69, 144, 145, 146, 147),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^22^FRI^1530-1720^TR+108^Teaching Wk2-13",
                    },
                    {
                        "index": "00702",
                        "schedule": self.get_schedule_str(68, 69, 144, 145, 146, 147),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^23^FRI^1530-1720^TR+30^Teaching Wk2-13",
                    },
                    {
                        "index": "00703",
                        "schedule": self.get_schedule_str(68, 69, 144, 145, 146, 147),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^24^FRI^1530-1720^TR+107^Teaching Wk2-13",
                    },
                    {
                        "index": "00704",
                        "schedule": self.get_schedule_str(68, 69, 134, 135, 136, 137),
                        "information": "LEC/STUDIO^1^WED^0930-1020^ONLINE^;TUT^25^FRI^1030-1220^TR+31^Teaching Wk2-13",
                    },
                ],
                "common_schedule": self.get_schedule_str(68, 69),
            }
        ])
