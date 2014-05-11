/*
The MIT License (MIT)

Copyright (c) 2014 Hu Dou 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

var app = require('http').createServer(handler)
  , io = require('socket.io').listen(app)
  , fs = require('fs')
  , url = require('url')
  , exec = require('child_process').exec
  , zmq = require('zmq')

// Start the zeromq client to communicate with the motor control server
zmqsocket = zmq.socket('pair')
zmqsocket.connect('tcp://localhost:5555') 

// Node server, listening to port 8088
app.listen(8088);

function handler (req, res) {
  var pathname = url.parse(req.url).pathname;
  console.log('request ' + pathname);

  if (pathname == '/')
    pathname = '/index.html';

  fs.readFile(__dirname + pathname,
  function (err, data) {
    if (err) {
      res.writeHead(500);
      return res.end('Error loading ' + pathname);
    }

    res.writeHead(200);
    res.end(data);
  });
}

zmqsocket.on('message', function(resp) {
  console.log('Motor server response: ' + resp);
});

io.sockets.on('connection', function (socket) {
  socket.on('control event', function (data) {
    console.log(data);
    var op = data['op'];
    zmqsocket.send(op);
  });
});


