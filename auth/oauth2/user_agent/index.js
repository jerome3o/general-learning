// fetch data from localhost:8000/user/data and put json output in user-data
// fetch("http://localhost:8000/user/data", { credentials: "include" })
//   .then(function (response) {
//     return response.json();
//   })
//   .then(function (json) {
//     document.getElementById("user-data").innerHTML = JSON.stringify(
//       json,
//       null,
//       4
//     );
//   });

// the above snippet adapted to use await

async function getResponse() {
  let response = await fetch("http://localhost:8000/user/data", {
    credentials: "include",
  });
  // if redirect
  if (response.redirected) {
    window.location.href = response.url;
    return;
  }
  console.log(response);

  let json = await response.json();
  document.getElementById("user-data").innerHTML = JSON.stringify(
    json,
    null,
    4
  );
}
getResponse();
