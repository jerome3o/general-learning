function submitForm(event) {
  event.preventDefault();

  const form = document.getElementById("login-form");

  const username = form.querySelector("#username").value;
  const password = form.querySelector("#password").value;

  // get query parameters for current page
  const urlParams = new URLSearchParams(window.location.search);
  // allow defaults
  const redirect_uri = urlParams.get("redirect_uri") ?? "default_callback";
  const client_id = urlParams.get("client_id") ?? "default_client_id";
  const response_type = urlParams.get("response_type") ?? "default_code";

  const jsonData = {
    redirect_uri,
    client_id,
    response_type,
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
