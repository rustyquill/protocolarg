

let searchForm = document.getElementById("searchForm");
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

function parseForm(formObject) {

  let formData = [];
  for (i = 1; i <= 10; i++) {
    var buttonValue = $(":input[name=row" + i + "]:checked").val();
    if (buttonValue != undefined) {
      formData.push(buttonValue);
    }
  }
  return formData;
}

function queryDatabase(formData) {

  let queryString = formData.join(',');
  let searchParams = new URLSearchParams(window.location.search);
  searchParams.append('query', queryString);
  let queryDestination = '/query.html?' + searchParams.toString()

  $.getJSON( queryDestination, function( data ) {
    if (data.success) {
      let searchProgressBody = document.getElementById('search-progress-body');
      searchProgressBody.innerHTML = '<p>Found ' + data.results + ' entrie(s).<p><p><a href="/results.html?nonce='+ data.nonce +'">Click Here to View Search Result(s)</a></p>';
    } else {
      let searchProgressBody = document.getElementById('search-progress-body');
      searchProgressBody.innerHTML = '<p>' + data.error + '</p><p><a href="/index.html">Refine search query</a></p>';
    }
  });
}

function search() {
  $("div.search-progress").show();
  let searchProgressBody = document.getElementById('search-progress-body');
  searchProgressBody.innerHTML = 'Searching .';

  let intervalId = setInterval(frame, 250);
  let intervalCounter = 0;
  let maxIntervalCounter = randomIntFromInterval(10,20)
  function frame() {
    if (intervalCounter > maxIntervalCounter) {
      clearInterval(intervalId);
      let formData = parseForm(searchForm);
      queryDatabase(formData);
      return
    }
    intervalCounter++;
    if (intervalCounter % 4 == 0) {
      searchProgressBody.innerHTML = 'Searching .';
    }
    else if (intervalCounter % 4 == 1) {
      searchProgressBody.innerHTML = 'Searching ..';
    }
    else if (intervalCounter % 4 == 2) {
      searchProgressBody.innerHTML = 'Searching ...';
    }
    else if (intervalCounter % 4 == 3) {
      searchProgressBody.innerHTML = 'Searching ....';
    } else {
      searchProgressBody.innerHTML = 'Searching .';
    }
  }
}

searchForm.addEventListener("submit", (e) => {
  e.preventDefault();
  search();
});
showLoad();
