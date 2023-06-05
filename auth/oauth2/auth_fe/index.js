function submitForm(event) {
  event.preventDefault();

  const form = document.getElementById("login-form");

  const username = form.querySelector("#username").value;
  const password = form.querySelector("#password").value;

  const jsonData = {
    // todo get from query parameters
    redirect_uri: "http://localhost:8000/oauth2/callback",
    client_id: "client_id",
    response_type: "code",
  };

  // fetch /oauth2/authorize, jsonify response and set innerhtml of "response" element
  fetch("/oauth2/authorize", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Basic " + btoa(username + ":" + password),
    },
    body: JSON.stringify(jsonData),
  })
    .then((response) => {
      return response.json();
    })
    .then((data) => {
      document.getElementById("response").innerHTML = JSON.stringify(
        data,
        null,
        4
      );
    })
    .catch((error) => {
      console.error("Error:", error);
    });
}
