// <span id="indexjs-loaded"></span>
// make the span say "index.js loaded {date}"
document.getElementById("indexjs-loaded").innerHTML =
  "index.js loaded " + new Date();

// add seconds since loadded to the span
// <p id="seconds-since-loaded"></p>
let start = new Date();

setInterval(function () {
  document.getElementById("seconds-since-loaded").innerHTML =
    "seconds since loaded: " + Math.floor((new Date() - start) / 1000);
}, 1000);

let worker = new Worker("pyodideWorker.js");
worker.onmessage = function (event) {
  console.log(event.data);

  // <div id="python-outputs"></div>
  // add the output.results to the div in a new line, if it's not undefined
  console.log(event.data);

  if (event.data.results !== undefined) {
    document.getElementById("python-outputs").innerHTML +=
      event.data.results + "<br>";
    console.log(event.data.results);
  }
  if (event.data.error !== "undefined") {
    document.getElementById("python-outputs").innerHTML +=
      event.data.error + "<br>";
    console.log(event.data.error);
  }
};

// <textarea id="python-code" cols="30" rows="10"></textarea>
// <button id="run-python-code">Run Python Code</button>

// on button click send message to worker
document.getElementById("run-python-code").onclick = function () {
  let python = document.getElementById("python-code").value;
  worker.postMessage({ python });
};

// fetch content from /static/py/main.py
fetch("/static/py/main.py")
  .then(function (response) {
    return response.text();
  })
  .then(function (startingCode) {
    document.getElementById("python-code").value = startingCode;
  });
