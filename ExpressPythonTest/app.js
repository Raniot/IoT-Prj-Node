const express = require('express')
const app = express()
const port = 3000

const spawn = require("child_process").spawn;
const pythonProcess = spawn('python',["script.py"]);

pythonProcess.stdout.on('data', (data) => {
  // Do something with the data returned from python script
  console.log(data.toString());
  test = data.toString()
});


app.get('/', (req, res) => {

	
	res.send('Hello World!' + test)
})


app.listen(port, () => console.log(`Example app listening on port ${port}!`))