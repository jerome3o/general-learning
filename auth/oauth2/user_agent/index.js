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

fetch("http://localhost:8001/")
  .then(function (response) {
    // get client-info p element and set its innerHTML to the response
    return response.json();
  })
  .then(function (json) {
    // format
    document.getElementById("server-info").innerHTML = JSON.stringify(
      json,
      null,
      4
    );
  });

// button with id: test-basic-auth
// output with id: basic-auth-result
// on button press fetch http://localhost:8000/privileged-info
// put the response in basic-auth-result
document
  .getElementById("test-basic-auth")
  .addEventListener("click", function () {
    fetch("http://localhost:8000/client-privileged-info")
      .then(function (response) {
        return response.json();
      })
      .then(function (json) {
        document.getElementById("basic-auth-result").innerHTML = JSON.stringify(
          json,
          null,
          4
        );
      });
  });
