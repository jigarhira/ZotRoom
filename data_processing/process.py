'''*************/
/* Zot Room    */
/* Version 1.0 */
/* Jigar Hira  */
/* April 2019  */
/*************'''

from bs4 import BeautifulSoup

from scrape import startSession, getDepartments, getDepartmentClasses

MAX_CLASS_DURATION = 30


def getClassData():
    # complete class data
    data = []

    # start webscraping session
    session = startSession()

    # get the current list of departments
    departments = generateDepartments(getDepartments(session).text)

    count = 0
    for department in departments:
        print('Getting '+ department + ' classes.')

        # get the data from each department and add it to the data array
        classes = extractClasses(getDepartmentClasses(session, department).text)
        data += classes[0]
        count += classes[1]

    print('\n-----------------\n    -~DONE~-\n-----------------\nFound ' + str(count) + ' classes in total.')
    return data


# extracts classes from html
def extractClasses(html_data):
    classes = []

    # parse html
    soup = BeautifulSoup(html_data, 'html.parser')

    # find all class entries
    count = 0
    for course in soup.find_all('tr', valign='top'):                    # search for table entries
        if course.get('bgcolor') != '#fff0ff':                          # filter out the class headers
            if 'TBA' not in course.contents[5].text:                    # ignore classes without a time
                time_raw = course.contents[5].text                      # get the raw time string

                time = processTime(time_raw)                            # parse the time string
                room = course.contents[6].text.strip().lower()    # parse the room string

                classes = writeClasses(time, room, classes)

            count += 1

    print('Found ' + str(count) + ' classes.\n')

    return classes, count

# write the class entries to an array
def writeClasses(time, room, array):
    array.append([time['dotw'], time['time_start'], time['time_end'], room])
    return array

# process the terrible WebSoc time data
def processTime(time_raw):
    time = time_raw.split('-')                          # split the start and end time
    day_split = time[0].split('\xa0')                   # split the days and start time
    dotw = day_split[0].strip()                         # clean the days of the week
    time_start = day_split[len(day_split) - 1].strip()  # clean the start time
    time_end = time[len(time) - 1].strip()              # clean the end time

    # check if the class is in pm
    pm = False
    if 'p' in time_end:
        pm = True

    # convert time to decimal
    time_start = decimalTime(time_start)
    time_end = decimalTime(time_end)

    # military time adjustment
    if pm:
        if time_end < 72:
            time_end += 72
        if time_end - time_start > MAX_CLASS_DURATION:
            time_start += 72

    return {'dotw': dotw, 'time_start': time_start, 'time_end': time_end}


# convert string time to 24 hour decimal
def decimalTime(time_string):
    # get the hour from the time
    hour = int(time_string.split(':')[0])

    # get the minutes
    minutes = int(time_string.split(':')[1].split('p')[0]) / 10

    # combine the time
    time = (hour * 6) + int(minutes)

    return time


# generate a list of departments from html
def generateDepartments(html_data):
    departments = []    # array of departments

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
        departments.append(option.get('value'))
        count += 1

    # remove the first entry
    departments.pop(0)
    count -= 1

    print('Found ' + str(count) + ' departments.\n')
    return departments


# creates a dictionary of avalible rooms at given times
def getTimes(data):
    rooms = []  # list of rooms
    data_copy = data

    # add all the rooms to the list
    for entry in data:
        rooms.append(entry[3])

    # remove duplicate rooms
    rooms = list(dict.fromkeys(rooms))

    # Create the dictionary
    occupied = []
    for room in rooms:                      # iterate through the rooms
        for i in range (0, len(data_copy)): # for each room iterate through the data
            if data[i][4] == room:          # if the room matches
                pass




# creates a dictionary of availible times for given rooms
def getRooms():
    pass


def unit():
    for entry in getClassData():
        print(entry)

if __name__ == '__main__':
    unit()

''' EOF '''
