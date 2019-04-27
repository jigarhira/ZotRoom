var http = require("http");

// Make the server
http.createServer(function(request, response){
  // HTTP header, HTTP Status: 200 : OK
  response.writeHead(200, {'Content-Type': 'text/plain'});
  response.end('test');

}).listen(8080);

console.log('Servere running at http://127.0.0.1:8080/');
