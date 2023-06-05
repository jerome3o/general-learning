async function submitForm(event) {
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

  let resp = await fetch("/oauth2/authorize", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: "Basic " + btoa(username + ":" + password),
    },
    body: JSON.stringify(jsonData),
  });
  console.log(resp);
  // if resp is redirect, redirect to redirect_uri
  if (resp.redirected) {
    window.location.href = resp.url;
  } else {
    let json = await resp.json();
    let formattedJson = JSON.stringify(json, null, 4);
    document.getElementById("response").innerHTML = formattedJson;
  }
}
