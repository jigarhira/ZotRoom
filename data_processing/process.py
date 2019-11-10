'''
Zot Room
Version 1.0
Jigar Hira
April 2019
'''

from typing import List
from bs4 import BeautifulSoup
import json
import numpy as np
import re

import scrape
from scrape import WebSoc


class Departments:
    """
    Stores and parses the valid departments from WebSoc
    """

    def __init__(self):
        self.list = []  # list of departments

    def generate_list(self, html_data: str):
        """
        DOCSTRING
        """

        # parse the html
        soup = BeautifulSoup(html_data, 'html.parser')

        # find the Department menu
        count = 0
        menus = soup.find_all('select')
        for menu in menus:
            if menu.get('name') == 'Dept':
                break
        # add all the values to the array
        options = menu.find_all('option')
        for option in options:
            self.list.append(option.get('value'))
            count += 1

        # remove the first entry
        self.list.pop(0)
        count -= 1

        print('Found ' + str(count) + ' departments.\n')


class Course:
    """
    Object to store data for a course.
    """

    def __init__(self, dotw='', time_start=None, time_end=None, room=''):
        """
        Initialize Course object with given attributes.
        """
        self.dotw = dotw
        self.time_start = time_start
        self.time_end = time_end
        self.room = room


class CourseData:
    """
    Object to store all of the courses
    """

    def __init__(self):
        """
        Initializes CourseData structure.
        """
        self.courses = []

    def add_courses(self, new_courses: List[Course]):
        """
        Concatenates new courses to current list of courses
        """
        self.courses = self.courses + new_courses


class CourseExtractor:
    """
    Parses and decodes html into Course objects.
    """

    MAX_CLASS_DURATION = 30

    def extract_courses(self, html_data) -> List[Course]:
        """
        Parses courses for html data and returns the list of courses.
        """

        # List of courses
        courses = []

        # parse html
        soup = BeautifulSoup(html_data, 'html.parser')

        # find all class entries
        for course in soup.find_all('tr', valign='top'):  # search for table entries
            if course.get('bgcolor') != '#fff0ff':  # filter out the class headers
                if 'TBA' not in course.contents[5].text:  # ignore classes without a time
                    time_raw = course.contents[5].text  # get the raw time string

                    time = self.__parse_time(time_raw)  # parse the time string
                    dotw = time[0]
                    time_start = time[1]
                    time_end = time[2]
                    room = course.contents[6].text.strip().lower()  # parse the room string

                    # Add Course object to list
                    courses.append(Course(dotw=dotw, time_start=time_start, time_end=time_end, room=str(room)))

        print('Found ' + str(len(courses)) + ' classes.\n')

        return courses

    def __parse_time(self, time_raw: str) -> (str, str, str):
        """
        Parses the raw time into the correct format.
        """

        time = time_raw.split('-')  # split the start and end time
        day_split = time[0].split('\xa0')  # split the days and start time
        dotw = day_split[0].strip()  # clean the days of the week
        time_start = day_split[len(day_split) - 1].strip()  # clean the start time
        time_end = time[len(time) - 1].strip()  # clean the end time

        # check if the class is in pm
        pm = False
        if 'p' in time_end:
            pm = True

        # convert time to decimal
        time_start = self.__integer_time(time_start)
        time_end = self.__integer_time(time_end)

        # military time adjustment
        if pm:
            if time_end < 72:
                time_end += 72
            if time_end - time_start > self.MAX_CLASS_DURATION:
                time_start += 72

        return dotw, time_start, time_end

    def __integer_time(self, time_string: str) -> int:
        """
        Converts time string to 24 hour integer
        """
        # get the hour from the time
        hour = int(time_string.split(':')[0])

        # get the minutes
        minutes = int(time_string.split(':')[1].split('p')[0]) / 10

        # combine the time
        time_int = (hour * 6) + int(minutes)

        return time_int


def generate_free_rooms(room_times: dict) -> dict:
    """
    Generates data structure for getting free rooms for each time.
    """
    # create data format
    free_rooms = {'M': {},
                  'Tu': {},
                  'W': {},
                  'Th': {},
                  'F': {}
                  }
    # add empty lists for each time
    for dotw in free_rooms:
        for i in range(0,  144):
            free_rooms[dotw][i] = []

    # iterate through all the rooms. days, and times
    for room in room_times:
        for day in room_times[room]:
            for time in room_times[room][day]:
                # add the room to the corresponding time
                free_rooms[day][time].append(room)

    return free_rooms


def generate_room_times(course_data: CourseData) -> dict:
    """
    Generates data structure for getting the room availability.
    """
    room_time = {}
    # iterate through all the courses
    for course in course_data.courses:
        # checks if room does not already have an entry
        if course.room not in room_time:
            # create the data format
            room_time[course.room] = {'M': [],
                                      'Tu': [],
                                      'W': [],
                                      'Th': [],
                                      'F': []
                                      }
        # get the dotw for the class and iterate through
        dotw = re.findall('[A-Z][^A-Z]*', course.dotw)

        # check for Saturday or Sunday classes
        if 'Sa' in dotw:
            dotw.remove('Sa')
        if 'Su' in dotw:
            dotw.remove('Su')

        for day in dotw:
            # Add class time tuple to data structure
            room_time[course.room][day].append((course.time_start, course.time_end))

    # parse class times for each room into availability
    # iterate through rooms and days
    for room in room_time:
        for day in room_time[room]:
            # generate list of available times
            available_time = [i for i in range(0, 144)]
            # iterate each class tuple in each room and day
            for class_time in room_time[room][day]:
                for time in range(class_time[0], class_time[1]):
                    # remove entries from available time
                    if time in available_time:
                        available_time.remove(time)
            # replace old time entry
            room_time[room][day] = available_time

    return room_time


# process.py unit test
def unit():
    # Create WebSoc object for handling http requests
    websoc = WebSoc(url=scrape.URL, header=scrape.HTTP_HEADER, payload=scrape.HTTP_PAYLOAD)

    # Initialize Departments object and generate list of vaild departments
    departments = Departments()
    departments.generate_list(websoc.get_departments().text)

    # Initialize CourseData object to store the total course list
    course_data = CourseData()

    # Iterate through all valid departments
    for department in departments.list:
        print('Getting ' + department + ' courses:')

        # Get the html response for the department
        courses_html = websoc.get_department_classes(department).text

        # Parse html response and extract courses for the department
        course_extractor = CourseExtractor()
        courses = course_extractor.extract_courses(courses_html)

        # Add courses to total course list
        course_data.add_courses(courses)

    print('-----------------\n    -~DONE~-\n-----------------\nFound ' + str(
        len(course_data.courses)) + ' classes in total.')

    # Generate room availability
    room_times = generate_room_times(course_data)

    # Generate free rooms for a given time
    free_rooms = generate_free_rooms(room_times)

    with open('room_times.json', 'w') as outfile:
        json.dump(room_times, indent=4, fp=outfile)
    with open('free_rooms.json', 'w') as outfile:
        json.dump(free_rooms, indent=4, fp=outfile)


if __name__ == '__main__':
    unit()

''' EOF '''
