

function cft() {
  let intervalId = setInterval(frame, 1000);
  let intervalCounter = 0;
  function frame() {
    if (intervalCounter > 0) {
      clearInterval(intervalId);
      return
    }
    confetti({
      particleCount: 80,
      spread: 70,
      origin: { y: 0.6 },
    });
    intervalCounter++;
  }
}

cft();
document.cookie = "arg-finale-visited=true; expires=Fri, 5 Jan 2024 23:59:59 GMT";
