//Если dislike == true, вывести треки с кнопкой дислайка (крестиком).
async function show_music(tracks, nickname, dislike = false) {
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
    if (typeof track["cover"] !== 'undefined'){
      album_box.style.backgroundImage = "url(" + track["cover"] + ")";
    }
    else{
      album_box.style.backgroundImage = "url(/static/home/img/no-cover.jpg)"; 
    }

    /* КНОПКИ РЕАКЦИИ ПОЛЬЗОВАТЕЛЯ */
      /* КНОПКА ЛАЙКА */

    var heartCircle = document.createElement('div');
    heartCircle.classList.add('heart-Circle');
    heartCircle.setAttribute('role', 'checkbox');
    heartCircle.setAttribute('aria-checked', 'false');
    heartCircle.setAttribute('title', 'Нравится')
    var leftSide = document.createElement('div');
    leftSide.classList.add('left-Side', 'sides');
    var rightSide = document.createElement('div');
    rightSide.classList.add('right-Side', 'sides');
    var heart1 = document.createElement('div');
    heart1.classList.add('heart');
    var half1 = document.createElement('div');
    half1.classList.add('half');
    half1.appendChild(heart1);
    var heart2 = document.createElement('div');
    heart2.classList.add('heart');
    var half2 = document.createElement('div');
    half2.classList.add('half');
    half2.appendChild(heart2);
    var heartContainer = document.createElement('div');
    heartContainer.classList.add('heart-Container');

    heartContainer.appendChild(leftSide);
    heartContainer.appendChild(rightSide);
    leftSide.appendChild(half1);
    rightSide.appendChild(half2);
    heartCircle.appendChild(heartContainer);
  
  
    if (dislike == true) {
        /* КНОПКА ДИЗЛАЙКА */
      var crossCircle = document.createElement('div');
      crossCircle.classList.add('cross-Circle');
      crossCircle.setAttribute('role', 'checkbox');
      crossCircle.setAttribute('aria-checked', 'false');
      crossCircle.setAttribute('title', 'Больше не рекомендовать')
      var crossContainer = document.createElement('div');
      crossContainer.classList.add('cross');

      
      crossCircle.appendChild(crossContainer);
    }
  
        /* СБОР ТРЕКА */
    element.appendChild(song_box);
    element.appendChild(heartCircle);
    if (dislike == true) {
      element.appendChild(crossCircle);
    }
    element.appendChild(album_box);
    document.getElementById("user_tracks").appendChild(element);
  
  }
  set_like_listeners(nickname);
  if (dislike == true) {
    set_dislike_listeners(nickname);
  }
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

show_music(tracks = tracks, nickname = nickname);



}

async function like_handler(button, nickname){

  console.log(nickname);
  // console.log(button.value);

  if( button.getAttribute('aria-checked') === "false"){
    button.setAttribute('aria-checked', 'true');
    button.setAttribute('title', 'Не нравится')
  }
  else{
    button.setAttribute('aria-checked', 'false');
    button.setAttribute('title', 'Нравится')
  }

  var track_box = button.closest(".list_element");
  var song_info = track_box.querySelector(".song_box");
  var song_name = song_info.querySelector(".song_name");
  var song_artist = song_info.querySelector(".song_artist");

  //УБЕДИТЬСЯ ЧТО ОН УДАЛЯЕТСЯ ИЗ дизлайкнутых
  var cross = track_box.querySelector(".cross-Circle")
  if (cross != null){
    cross.setAttribute('aria-checked', 'false');
    cross.setAttribute('title', 'Нравится')
  }


  console.log(song_name.innerText)

  const response_like_handler = await fetch("/music/clickLike/", {
    method: "POST",
    headers: { "Accept": "application/json" },
    body: JSON.stringify({
      nickname : nickname,
      song_name : song_name.innerText,
      song_artist : song_artist.innerText
      })
    });

    console.log(response_like_handler);
    if (response_like_handler.ok === true) {
      return true;
    }
    else {
      const text = await response_like_handler.text();
      return false;
    }
}


async function dislike_handler(button, nickname){

  console.log(nickname);

  if( button.getAttribute('aria-checked') === "false"){
    button.setAttribute('aria-checked', 'true');
    button.setAttribute('title', 'Рекомендовать')
  }
  else{
    button.setAttribute('aria-checked', 'false');
    button.setAttribute('title', 'Больше не рекомендовать')
  }

  var track_box = button.closest(".list_element");
  var song_info = track_box.querySelector(".song_box");
  var song_name = song_info.querySelector(".song_name");
  var song_artist = song_info.querySelector(".song_artist");


  //УБЕДИТЬСЯ ЧТО ОН УДАЛЯЕТСЯ ИЗ БИБЛИОТЕКИ
  var heart = track_box.querySelector(".heart-Circle")
  heart.setAttribute('aria-checked', 'false');
  heart.setAttribute('title', 'Нравится')


  console.log(song_name.innerText)

  const response_dislike_handler = await fetch("/music/clickDislike/", {
    method: "POST",
    headers: { "Accept": "application/json" },
    body: JSON.stringify({
      nickname : nickname,
      song_name : song_name.innerText,
      song_artist : song_artist.innerText
      })
    });

    console.log(response_dislike_handler);
    if (response_dislike_handler.ok === true) {
      return true;
    }
    else {
      const text = await response_dislike_handler.text();
      return false;
    }
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


  show_music(tracks = tracks, nickname = nickname, dislike = true);
}

async function set_like_listeners(nickname){

  var hrts = document.querySelectorAll('.heart-Circle');

  for (var i = 0; i < hrts.length; i++) {
    hrts[i].addEventListener("click", (function(button) {
      return function() {
        like_handler(button, nickname);
      }
    })(hrts[i]));
  }

}

async function set_dislike_listeners(nickname){

  var crsss = document.querySelectorAll('.cross-Circle');

  for (var i = 0; i < crsss.length; i++) {
    crsss[i].addEventListener("click", (function(button) {
      return function() {
        dislike_handler(button, nickname);
      }
    })(crsss[i]));
  }

}


async function setup_user_page(nickname){
  // document.getElementById("music_link").style.display = "none";
  document.getElementById("settings_link").style.display = "none";
  document.getElementById("subscriptions_link").style.display = "none";
  document.getElementById("music_search_field").value = "";
  
  console.log("LIST_USER_TRACKS");
  const response_fav_tracks = await fetch("/music/getUserFavouriteTracks/?nickname=" + nickname, {
    headers: { "Accept": "application/json" }
  });

  var tracks = await response_fav_tracks.json();

  document.getElementById("user_tracks").innerHTML = "";
  document.getElementById("user_recomendations").innerHTML = "";

  show_music(tracks = tracks, nickname = nickname);

  var hrts = document.querySelectorAll('.heart-Circle');
  for (var i = 0; i < hrts.length; i++) {
    hrts[i].setAttribute('aria-checked', 'true');
    hrts[i].setAttribute('title', 'Не нравится')
  }

}


async function get_search_results(nickname) {

  document.getElementById("user_page_header").innerText = "РЕЗУЛЬТАТЫ ПОИСКА";
  document.getElementById("user_tracks").innerHTML = "";
  document.getElementById("user_recomendations").innerHTML = "";
  
  console.log("GET_SEARCH_RESULTS");
  
  var track_name = document.getElementById("music_search_field").value;
  console.log("Finding \"" + track_name + "\"");

  const response_recomendation = await fetch("/music/findTrack?" + new URLSearchParams({
    nickname : nickname,
    track_name: track_name
  }),
  {
    headers: { "Accept": "application/json" }
  });
  
  
  var tracks = await response_recomendation.json();

  // console.log(tracks)
  show_music(tracks = tracks, nickname = nickname);

  var hrts = document.querySelectorAll('.heart-Circle');
  for (var i = 0; i < hrts.length; i++) {
    if (tracks[i]["in_favourite"] == true){
      hrts[i].setAttribute('aria-checked', 'true');
      hrts[i].setAttribute('title', 'Не нравится')
    }
  }

}  