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

console.log("IMPORT_TRACKS");

document.getElementById("user_page_header").innerText = "ИМПОРТИРОВАННАЯ БИБЛИОТЕКА"

const response_lastfm_nick = await fetch("/users/lastfm_nick", {
method: "POST",
headers: { "Accept": "application/json" },
body: JSON.stringify({
  nickname : nickname
  })
});

var lastFmNickname = await response_lastfm_nick.text();

try {
const response_integrate = await fetch("/music/lastFM-integration/", {
method: "POST",
headers: { "Accept": "application/json" },
body: JSON.stringify({
  nickname : nickname,
  lastFmNickname : lastFmNickname
  })
});

}
catch{}

const response_fav_tracks = await fetch("/music/getUserFavouriteTracks/?nickname=" + nickname, {
  headers: { "Accept": "application/json" }
});

var tracks = await response_fav_tracks.json();


document.getElementById("user_tracks").innerHTML = "";
document.getElementById("user_recomendations").innerHTML = "";


for (var obj in tracks) {
  
  var track = tracks[obj];

      /* ТРЕК В СПИСКЕ РЕКОМЕНДОВАННЫХ */
  var element = document.createElement("div");
  element.className = "list_element";

      /* ИНФОРМАЦИЯ О ТРЕКЕ */
  var song_box = document.createElement("div");
  song_box.className = "song_box";

  var song_name = document.createElement("li");
  song_name.className = "song_info song_name";
  song_name.innerText = track["name"];

  var song_artist = document.createElement("li");
  song_artist.className = "song_info song_artist";
  song_artist.innerText = track["artist"];

  if (typeof track["album"] !== 'undefined') {
    var song_album = document.createElement("li");
    song_album.className = "song_info song_album";
    song_album.innerText = track["album"];
  }

  song_box.appendChild(song_name);
  song_box.appendChild(song_artist);

  if (typeof song_album !== 'undefined') {
    song_box.appendChild(song_album);
  }

      /* ОБЛОЖКА АЛЬБОМА */

  var album_box = document.createElement("div");
  album_box.className = "album_box";

      /* СБОР ТРЕКА */
  element.appendChild(song_box);
  element.appendChild(album_box);
  document.getElementById("user_tracks").appendChild(element);
}




}

async function like_handler(button, nickname){

console.log(nickname);
console.log(button.value);
if(button.value == 0) {
  button.value = 1;
  button.style.backgroundColor =  "#FF8E00";
  //не знаю хули не работает, потом разберусь
  button.style.setProperty('--after-bg-color', "#FF8E00");
  button.style.setProperty('--before-bg-color', "#FF8E00");
}
else{
  button.value = 0;
  button.style.backgroundColor =  "#000000";
  //не знаю хули не работает, потом разберусь
  button.style.setProperty('--before-bg-color', "#000000");
  button.style.setProperty('--after-bg-color', "#000000");
}

var track_box = button.closest(".list_element");
var song_info = track_box.querySelector(".song_box");
var song_name = song_info.querySelector(".song_name");
var song_artist = song_info.querySelector(".song_artist");

const response_like_handler = await fetch("/music/clickLike/", {
  method: "POST",
  headers: { "Accept": "application/json" },
  body: JSON.stringify({
    nickname : nickname,
    song_name : song_name.innerText,
    song_artist : song_artist.innerText
    })
  });

  if (response_like_handler.ok === true) {
    return true;
  }
  else {
    const text = await response_like_handler.text();
    log.console(text)
    return false;
  }
  console.log(song_name.innerText)
}

async function get_recomendations(nickname) {

document.getElementById("user_page_header").innerText = "РЕКОМЕНДАЦИИ ДЛЯ ВАС";

console.log("GET_RECOMMENDATIONS");


const response_recomendation = await fetch("/music/getRecommendations?" + new URLSearchParams({
  nickname: nickname,
  amount: 10,
}),
{
  headers: { "Accept": "application/json" }
});


var tracks = await response_recomendation.json();

document.getElementById("user_tracks").innerHTML = "";
document.getElementById("user_recomendations").innerHTML = "";


for (var obj in tracks) {
  var track = tracks[obj];
  console.log(track);
      /* ТРЕК В СПИСКЕ РЕКОМЕНДОВАННЫХ */
  var element = document.createElement("div");
  element.className = "list_element";

      /* ИНФОРМАЦИЯ О ТРЕКЕ */
  var song_box = document.createElement("div");
  song_box.className = "song_box";

  var song_name = document.createElement("li");
  song_name.className = "song_info song_name";
  song_name.innerText = track["name"];

  var song_artist = document.createElement("li");
  song_artist.className = "song_info song_artist";
  song_artist.innerText = track["artist"];

  if (typeof track["album"] !== 'undefined') {
    var song_album = document.createElement("li");
    song_album.className = "song_info song_album";
    song_album.innerText = track["album"];
  }

  song_box.appendChild(song_name);
  song_box.appendChild(song_artist);

  if (typeof song_album !== 'undefined') {
    song_box.appendChild(song_album);
  }

      /* ОБЛОЖКА АЛЬБОМА */

  var album_box = document.createElement("div");
  album_box.className = "album_box";

      /* КНОПКИ РЕАКЦИИ */
  var button_box = document.createElement("div");
  button_box.className = "button_box";
  var like_button = document.createElement("button");
  like_button.className = "element reaction like_button";
  like_button.value = 0;
  // like_button.dataset.value = nickname;
  button_box.appendChild(like_button)

      /* СБОР ТРЕКА */
  element.appendChild(song_box);
  element.appendChild(button_box);
  element.appendChild(album_box);
  document.getElementById("user_tracks").appendChild(element);

}
set_listeners(nickname);
}

async function set_listeners(nickname){
var buttons = document.querySelectorAll(".reaction");
console.log(buttons.length);
for (var i = 0; i < buttons.length; i++) {
  buttons[i].addEventListener("click", (function(button) {
    return function() {
      like_handler(button, nickname);
    }
  })(buttons[i]));
}
}


async function list_user_tracks(nickname){
console.log("LIST_USER_TRACKS");
const response_fav_tracks = await fetch("/music/getUserFavouriteTracks/?nickname=" + nickname, {
  headers: { "Accept": "application/json" }
});

var tracks = await response_fav_tracks.json();

document.getElementById("user_tracks").innerHTML = "";
document.getElementById("user_recomendations").innerHTML = "";

for (var obj in tracks) {
  var track = tracks[obj];

      /* ТРЕК В СПИСКЕ РЕКОМЕНДОВАННЫХ */
  var element = document.createElement("div");
  element.className = "list_element";

      /* ИНФОРМАЦИЯ О ТРЕКЕ */
  var song_box = document.createElement("div");
  song_box.className = "song_box";

  var song_name = document.createElement("li");
  song_name.className = "song_info song_name";
  song_name.innerText = track["name"];

  var song_artist = document.createElement("li");
  song_artist.className = "song_info song_artist";
  song_artist.innerText = track["artist"];

  if (typeof track["album"] !== 'undefined') {
    var song_album = document.createElement("li");
    song_album.className = "song_info song_album";
    song_album.innerText = track["album"];
  }

  song_box.appendChild(song_name);
  song_box.appendChild(song_artist);

  if (typeof song_album !== 'undefined') {
    song_box.appendChild(song_album);
  }

      /* ОБЛОЖКА АЛЬБОМА */

  var album_box = document.createElement("div");
  album_box.className = "album_box";

      /* СБОР ТРЕКА */
  element.appendChild(song_box);
  element.appendChild(album_box);
  document.getElementById("user_tracks").appendChild(element);
}
}