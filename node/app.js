const express = require('express')
const app = express()
const port = 3000

const spawn = require("child_process").spawn;
const pythonProcess = spawn('python',["BackgroundSubtraction.py"]);

var people = 0

pythonProcess.stdout.on('data', (data) => {
  // Do something with the data returned from python script

  var integer = parseInt(data);
  people += integer
  // console.log(data.toString());
  // test = data.toString()
});


app.get('/', (req, res) => {
	res.send('Amount of people: ' + people.toString())
})


app.listen(port, () => console.log(`Example app listening on port ${port}!`))