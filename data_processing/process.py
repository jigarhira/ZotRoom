'''
Zot Room
Version 1.0
Jigar Hira
April 2019
'''

from typing import List
from bs4 import BeautifulSoup
import numpy as np

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

    def __init__(self, dotw='', time_start='', time_end='', room=''):
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
                    dotw = time
                    time_start = time[1]
                    time_end = time[2]
                    room = course.contents[6].text.strip().lower()  # parse the room string

                    # Add Course object to list
                    courses.append(Course(dotw=dotw, time_start=time_start, time_end=time_end, room=room))

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


# creates a dictionary of available times for a given room
def getTimes(data):
    rooms = []  # list of rooms

    # add all the rooms to the list
    for entry in data:
        rooms.append(entry[3])

    # remove duplicate rooms
    rooms = list(dict.fromkeys(rooms))

    # create the dictionary
    avalibility = {rooms[i]: np.zeros((5, 144), dtype=int) for i in range(0, len(rooms))}

    # enter the information from the data into the dictionary
    dotw = []  # array to store which days the class is scheduled
    for i in range(0, len(data)):  # iterating through entries
        if 'M' in data[i][0]:  # checking for each day of the week
            dotw.append(0)
        if 'Tu' in data[i][0]:
            dotw.append(1)
        if 'W' in data[i][0]:
            dotw.append(2)
        if 'Th' in data[i][0]:
            dotw.append(3)
        if 'F' in data[i][0]:
            dotw.append(4)
        for day in dotw:  # iterating through each applicable day
            for j in range(data[i][1], data[i][2]):  # iterating through all the occupied times
                avalibility[data[i][3]][day][j] = 1  # sets the time period to 1 (booked)
        dotw.clear()  # clears the dotw for the next entry

    return avalibility


# creates a dictionary of availible times for given rooms
def getRooms(data):
    times = []  # list of the times

    rooms = []  # list of the rooms

    # create the list of data in the following format:
    #   list of 5 lists (days of the week)
    #   list of 144 lists (10 minute blocks in the day)
    #   list of strings (rooms that are full or availible at that time)
    full = []
    availability = []
    for _ in range(0, 5):
        full.append([])
        availability.append([])
    for day in range(0, 5):
        for _ in range(0, 144):
            full[day].append([])
            availability[day].append([])

    # enter the data into availability
    dotw = []  # array to store which days the class is scheduled
    for entry in data:  # iterates through all of the classes

        if entry[3] not in rooms:  # checks to see if the room is in the room list
            rooms.append(entry[3])  # adds room to room list

        if 'M' in entry[0]:  # checking for each day of the week
            dotw.append(0)
        if 'Tu' in entry[0]:
            dotw.append(1)
        if 'W' in entry[0]:
            dotw.append(2)
        if 'Th' in entry[0]:
            dotw.append(3)
        if 'F' in entry[0]:
            dotw.append(4)
        for day in dotw:  # iterates through the days he class is scheduled
            for j in range(entry[1], entry[2]):  # iterates through the times that the class is in session
                if entry[3] not in full[day][j]:  # checks to see if the room was already added to that time
                    full[day][j].append(entry[3])  # add the room to the time
        dotw.clear()  # clears the dotw list

        # generates the availability list from the full list
        for day in range(0, 5):  # iterates through the days
            for time in range(0, 144):  # iterates through the times
                for room in rooms:  # iterates through the rooms
                    if room not in full[day][time]:  # checks if the room from the room list was in full for that time
                        if room not in availability[day][
                            time]:  # checks if the room is already in the availability list
                            availability[day][time].append(room)  # adds the room to the availability list

    return availability


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

    print('-----------------\n    -~DONE~-\n-----------------\nFound ' + str(len(course_data.courses)) + ' classes in total.')


if __name__ == '__main__':
    unit()

''' EOF '''
