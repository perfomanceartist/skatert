async function set_settings(nickname) {
  var lastFmNickname = document.getElementById("lastfm").value;
  var secondFactor = document.getElementById("CB").checked;

  var token = document.cookie.match(/token=(.+?)(;|$)/)[1];

  console.log(JSON.stringify({
      nickname : nickname,
      token: token,
      lastfm: lastFmNickname,
      secondFactor: secondFactor
  }));


  const response = await fetch("/api/settings", {
  method: "POST",
  headers: { "Accept": "application/json" },
  body: JSON.stringify({
      nickname : nickname,
      token: token,
      lastfm: lastFmNickname,
      secondFactor: secondFactor
  })
  });
  if (response.ok === true) {
  alert("Success!");
  }
  else alert("Error!")
}