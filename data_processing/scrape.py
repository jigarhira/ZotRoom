'''
Zot Room
Version 1.0
Jigar Hira
April 2019
'''

import requests

URL = 'https://www.reg.uci.edu/perl/WebSoc'

# header of the post request
http_header = {
    'Host' : 'www.reg.uci.edu',                         # domain
    'Origin' : 'https://www.reg.uci.edu',
    'Referer' : 'https://www.reg.uci.edu/perl/WebSoc',  # WebSoc url
    'Content-Type' : 'application/x-www-form-urlencoded'
}

# body of the POST request
http_payload = {
    'Submit': 'Display Web Results',  # type of results
    'YearTerm': '2019-14',  # quarter of classes
    'Breath': 'ANY',  # will not restrict to GE
    'Division': 'ANY',  # include graduate courses
    'ClassType': 'ALL',  # all classes
    'FullCourses': 'ANY',  # include full classes
    'CancelledCourses': 'Exclude',  # do not include cancelled classes
}


# create a session for requests
def startSession():
    # creates a session so we can reuse the same TCP connection
    session = requests.Session()

    # update default session header and payload to be reused
    session.headers.update(http_header)

    return session


# get the list of departments
def getDepartments(session):
    # HTTP GET request
    response = session.get(url=URL, headers={'Content-Type' : 'text/html'})

    # return the response
    return response


# return the list of classes for a department
def getDepartmentClasses(session, department):
    # department payload
    http_payload_department = {'Dept' : department}

    # HTTP POST request with payload
    response = session.post(url=URL, data=dict(http_payload, **http_payload_department))

    # return the response
    return response




# unit test
def unit():
    session = startSession()

    print(getDepartmentClasses(session, 'EECS').text)




if __name__ == "__main__":
    unit()

''' EOF '''