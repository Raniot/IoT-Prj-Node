const express = require('express')
const app = express()
const port = 3000
var mqtt = require('mqtt');
var client  = mqtt.connect('mqtt://84.238.67.87:2000');

const spawn = require("child_process").spawn;
const pythonProcess = spawn('python3',["BackgroundSubtraction.py"]);

var people = 0

pythonProcess.stdout.on('data', function(data) {
  console.log(data.toString());
  var integer = parseInt(data);
  people += integer
  
  message = '{"Sensors": [ { "Type": "Human counter", "Value": '+ integer +', "Unit": "humans" } ] }';

  jsonMessage = JSON.parse(message)
  client.publish('Gateway/message', jsonMessage); 
  console.log('Message Sent');
});

app.get('/', function(req, res) {
	res.send('Amount of people: ' + people.toString())
})

app.listen(port, function() {
  console.log('Example app listening on port: '+ port.toString())
})