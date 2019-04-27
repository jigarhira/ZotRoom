/***************/
/* Zot Room    */
/* Version 1.0 */
/* Jigar Hira  */
/* April 2019  */
/***************/

/* imports */
var http = require('http');
const request = require('request');
var cheerio = require('cheerio');

const options = {
  url: '',
  headers: {
    'Host' : 'www.reg.uci.edu',
    'Origin' : 'https://www.reg.uci.edu',
    'Referer' : 'https://www.reg.uci.edu/perl/WebSoc',
    'Content-Type' : 'application/x-www-form-urlencoded'
  },
  uri: 'https://www.reg.uci.edu/perl/WebSoc',
  body: 'Submit=Display+Web+Results&YearTerm=2019-14&ShowComments=on&ShowFinals=on&Breadth=ANY&Dept=CLT%26THY&CourseNum=&Division=ANY&CourseCodes=&InstrName=&CourseTitle=&ClassType=ALL&Units=&Days=&StartTime=&EndTime=&MaxCap=&FullCourses=ANY&FontSize=100&CancelledCourses=Exclude&Bldg=&Room=',
  method: 'POST'
};

var result;

request(options, function(error, response, body){
  console.error('error:', error); /* print error */
  console.log('status code:', response && response.statusCode); /* print response code if recieved */
  //console.log('body:', body); /* print the body */
  result = body;
});

result = cheerio.load(result);
//console.log(result('class=course-list').html());

/* make the server */
http.createServer(function(request, response){
  response.writeHead(200, {'Content-Type': 'text/html'});
  response.write(result);
  response.end();

}).listen(8080);

console.log('Server running at http://127.0.0.1:8080/');

/* EOF */
