'''
Zot Room
Version 1.0
Jigar Hira
April 2019
'''

import requests

URL = 'https://www.reg.uci.edu/perl/WebSoc'

# header of the post request
HTTP_HEADER = {
    'Host': 'www.reg.uci.edu',  # domain
    'Origin': 'https://www.reg.uci.edu',
    'Referer': 'https://www.reg.uci.edu/perl/WebSoc',  # WebSoc url
    'Content-Type': 'application/x-www-form-urlencoded'
}

# body of the POST request
HTTP_PAYLOAD = {
    'Submit': 'Display Web Results',  # type of results
    'YearTerm': '2019-92',  # quarter of classes
    'Breath': 'ANY',  # will not restrict to GE
    'Division': 'ANY',  # include graduate courses
    'ClassType': 'ALL',  # all classes
    'FullCourses': 'ANY',  # include full classes
    'CancelledCourses': 'Exclude',  # do not include cancelled classes
}

class WebSoc:
    """
    DOCSTRING
    """

    def __init__(self, url='', header={}, payload={}):
        """
        DOCSTRING
        """

        # set the constructor attributes
        self.url = url
        self.header = header
        self.payload = payload

        # creates a session so we can reuse the same TCP connection
        self.session = requests.Session()

        # update default session header and payload to be reused
        self.session.headers.update(self.header)

    def get_departments(self) -> requests.Response:
        """
        Requests a list of valid departments and returns the response.
        """

        # HTTP GET request
        return self.session.get(url=self.url, headers={'Content-Type ' : 'text/html'})

    def get_department_classes(self, department: str) -> requests.Response:
        """
        Requests the class data for a department and returns the response.
        """

        # department payload
        http_payload_department = {'Dept': department}

        # HTTP POST request with payload
        return self.session.post(url=self.url, data=dict(self.payload, **http_payload_department))


def unit():
    """
    Unit test
    """

    websoc = WebSoc(url=URL, header=HTTP_HEADER, payload=HTTP_PAYLOAD)

    print(websoc.get_department_classes('EECS').text)


if __name__ == "__main__":
    unit()

''' EOF '''