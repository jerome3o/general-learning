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

// Pyodide stuff, todo move to worker
let worker = new Worker("pyodideWorker.js");
worker.onmessage = function (event) {
  console.log(event.data);
  if (event.data === "pyodide loaded") {
    document.getElementById("pyodide-loaded").innerHTML =
      "pyodide loaded " + new Date();
  }
};

// <textarea id="python-code" cols="30" rows="10"></textarea>
// <button id="run-python-code">Run Python Code</button>

// on button click send message to worker
document.getElementById("run-python-code").onclick = function () {
  let python = document.getElementById("python-code").value;
  worker.postMessage({ python });
};
