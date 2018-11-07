const express = require('express')
const app = express()
const port = 3000

const spawn = require("child_process").spawn;
const pythonProcess = spawn('python',["script.py"]);

var people = 0

// pythonProcess.stdout.on('data', (data) => {
//   // Do something with the data returned from python script

//   var integer = parseInt(data);
//   people += integer
//   // console.log(data.toString());
//   // test = data.toString()
// });

pythonProcess.stdout.on('data', function(data) {
  // Do something with the data returned from python script
  // console.log(data.toString());
  var integer = parseInt(data);
  people += integer
});


app.get('/', function(req, res) {
	res.send('Amount of people: ' + people.toString())
})


app.listen(port, function() {
  console.log(`Example app listening on port ${port}!`)
})