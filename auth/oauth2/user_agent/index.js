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

// fetch data from localhost:8000/oauth2/info and put json output in login-with-auth-server-info
// Don't need the credentials: "include" option if hosted on same domain, should really just set up
// a proxy or configure CORS properly
fetch("http://localhost:8000/oauth2/info", { credentials: "include" })
  .then(function (response) {
    return response.json();
  })
  .then(function (json) {
    document.getElementById("login-with-auth-server-info").innerHTML =
      JSON.stringify(json, null, 4);

    // build authorization endpoint url, all json values are query parameters
    let url = new URL("http://localhost:8001/oauth2/authorize");
    // iterate over all the values in the json object and set them as query parameters
    for (const [key, value] of Object.entries(json)) {
      url.searchParams.append(key, value);
    }

    // set the button login-with-auth-server to direct the brower to the auth server
    document.getElementById("login-with-auth-server").href = url.toString();
  });

//
