fetch("http://localhost:8000/")
  .then(function (response) {
    // get client-info p element and set its innerHTML to the response
    return response.json();
  })
  .then(function (json) {
    // format
    document.getElementById("client-info").innerHTML = JSON.stringify(
      json,
      null,
      4
    );
  });
