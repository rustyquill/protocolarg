let loadIndicator = document.getElementById("load");
let loadInterval = randomIntFromInterval(2,5)*1000;
let intervalIdLoad = setInterval(showLoad, loadInterval);

function randomIntFromInterval(min, max) {
  return Math.floor(Math.random() * (max - min + 1) + min)
}

function showLoad() {
  let l = Math.floor(Math.random() * 100);
  loadIndicator.innerHTML = 'System Load: ' + String(l).padStart(2, '0') + '%';
}

function redirectErrorPage() {
  let intervalId = setInterval(frame, 250);
  let intervalCounter = 0;
  function frame() {
    if (intervalCounter > 12) {
      clearInterval(intervalId);
      let searchParams = new URLSearchParams(window.location.search);
      location.assign('/error.html?' + searchParams.toString());
      return
    }
    intervalCounter++;
  }
}

function renderResults() {
  let mainBody = document.getElementsByTagName('main')[0];
  mainBody.innerHTML = `
    <div class="container-fluid animation vh-100" style="background-image: url('/assets/pictures/85ad4ea0-700f-4c17-bcfb-3f5e44b84fd9.gif');">
    </div>
  </div>
  `
}

function animateResults() {
  let intervalId = setInterval(frame, 250);
  let intervalCounter = 0;
  function frame() {
    // let the interval run for around half a second before glitching
    if (intervalCounter > 2) {
      clearInterval(intervalId);
      $(function() {
        $(".animation").mgGlitch({
          destroy: false,
          glitch: true,
          scale: true,
          blend: true,
          blendModeType: "hue",
          glitch1TimeMin: 200,
          glitch1TimeMax: 400,
          glitch2TimeMin: 10,
          glitch2TimeMax: 100,
        });
      });
      redirectErrorPage();
      return
    }
    intervalCounter++;
  }
}



function retrieveResults() {
  let resultsBody = document.getElementById('results');
  resultsBody.innerHTML = 'Retrieving search results .';

  let intervalId = setInterval(frame, 250);
  let intervalCounter = 0;
  let maxIntervalCounter = randomIntFromInterval(5,10)
  function frame() {
    if (intervalCounter > maxIntervalCounter) {
      clearInterval(intervalId);
      renderResults();
      animateResults();
      return
    }
    intervalCounter++;
    if (intervalCounter % 4 == 0) {
      resultsBody.innerHTML = 'Retrieving search results .';
    }
    else if (intervalCounter % 4 == 1) {
      resultsBody.innerHTML = 'Retrieving search results ..';
    }
    else if (intervalCounter % 4 == 2) {
      resultsBody.innerHTML = 'Retrieving search results ...';
    }
    else if (intervalCounter % 4 == 3) {
      resultsBody.innerHTML = 'Retrieving search results ....';
    } else {
      resultsBody.innerHTML = 'Retrieving search results .';
    }
  }
}


showLoad();
retrieveResults();
