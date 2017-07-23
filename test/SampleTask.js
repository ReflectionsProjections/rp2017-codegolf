var readline = require('readline');
var answer = require('./answer.js');

var rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  terminal: false
});

rl.on('line', function (line) {
  const arg1 = line.charCodeAt(0);
  const arg2 = line.charCodeAt(1);
  console.log(answer.answer(arg1, arg2));
  process.exit();
});
