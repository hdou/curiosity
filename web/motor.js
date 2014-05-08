var app = require('http').createServer(handler)
  , io = require('socket.io').listen(app)
  , fs = require('fs')
  , url = require('url')
  , exec = require('child_process').exec

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

io.sockets.on('connection', function (socket) {
  socket.on('control event', function (data) {
    console.log(data);
    var op = data['op'];
    exec('sudo python ../scripts/motor.py ' + op, function(error, stdout, stderr) {
     console.log('stdout' + stdout);
     console.log('stderr' + stderr);
     if (error != null) {
       console.log(error);
     }
    });
  });
});

