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
