function generateRandomNegativeNumber() {
  var randomNegativeNumber = -Math.random() * 10000000;
  return randomNegativeNumber.toString();
}

function replaceContentOfRandomNumberDivWithRandomNumber() {
  var randomNumber = generateRandomNegativeNumber();
  document.getElementById("random-number").innerHTML = randomNumber;
}

function nntp() {
  const ip="13.???.???.??8:119"
  $.ajax({url: ip, error: function(xhr){

    console.error("Unable to connect to server nntp://" + ip + ". Invalid 🜶 address")
  }});
}

function conn() {
  nntp()
  let intervalId = setInterval(frame, 3000);
  let intervalCounter = 0;
  function frame() {
    // run for ~ 3 seconds
    if (intervalCounter > 20) {
      clearInterval(intervalId);
      return
    }
    intervalCounter++;
    nntp()
  }
}

function errcoun() {
  replaceContentOfRandomNumberDivWithRandomNumber()
  let intervalId = setInterval(frame, 3000);
  function frame() {
    replaceContentOfRandomNumberDivWithRandomNumber()
  }
}

errcoun()
conn()
