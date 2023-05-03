async function exit_account() {
    const response = await fetch("/api/logout", {
    method: "POST",
    headers: { "Accept": "application/json" }
  });
  if (response.ok === true) {
    window.location.replace('/login');
  }
  else alert("Error!")
}


async function import_tracks(nickname) {

  // console.log(nickname)

  const response_lastfm_nick = await fetch("/users/lastfm", {
  method: "POST",
  headers: { "Accept": "application/json" },
  body: JSON.stringify({
    nickname : nickname
    })
  });

  var lastFmNickname = await response_lastfm_nick.text();
  // console.log(lastFmNickname);

  try {
  const response_integrate = await fetch("/music/lastFM-integration/", {
  method: "POST",
  headers: { "Accept": "application/json" },
  body: JSON.stringify({
    nickname : nickname,
    lastFmNickname : lastFmNickname
    })
  });

  // var data = await response_integrate.json();
  // console.log(data)
  }
  catch{

  }

  const response_fav_tracks = await fetch("/music/getUserFavouriteTracks/?nickname=" + nickname, {
    headers: { "Accept": "application/json" }
  });

  var tracks = await response_fav_tracks.json();

  // console.log(tracks)

  for (var obj in tracks) {
    console.log(tracks[obj]);
    var track = tracks[obj];
    // var menu = main_category[i];

    var li = document.createElement("li");
    li.innerHTML = track["name"] + "---" + track["artist"] + "---" + track["album"];
    // li.innerHTML = tracks[track]["name"];
    document.getElementById("mylist").appendChild(li);
  }




}
 