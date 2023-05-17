var nickname_value = "";

async function set_listeners(){

  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  var button = document.getElementById("button_next");

  checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', () => {
      var result = false;
      checkboxes.forEach(cb => {
        if (cb.checked) {
          result = true;
        }
      });
      if (result === true){
        button.classList.remove('d-none');
      }
      else {
        button.classList.add('d-none');
      }
    });
  });


  var nickname_input = document.getElementById('lastfm_nickname');
  nickname_input.addEventListener("input", () => {
    if (nickname_input.value !== nickname_value) {
      button.classList.add("d-none");
    } else {
      button.classList.remove("d-none");
    }
  });



}

async function load_choice(){
  document.getElementById('button_next').value = undefined;
  
  document.getElementById("type_choosing").classList.remove('d-none');
  document.getElementById("choice_header").classList.remove('d-none');

  document.getElementById("genres_header").classList.add("d-none");
  document.getElementById("genres").classList.add("d-none");
  document.getElementById("action_choosing").classList.add("d-none");

  document.getElementById("lastfm_header").classList.add('d-none');
  document.getElementById("lastfm_container").classList.add('d-none');
}

async function load_genres(){

  document.getElementById('button_next').value = "genres";

  document.getElementById("type_choosing").classList.add('d-none');
  document.getElementById("choice_header").classList.add('d-none');

  document.getElementById("genres_header").classList.remove("d-none");
  document.getElementById("genres").classList.remove("d-none");

  document.getElementById("action_choosing").classList.remove("d-none");
}

async function load_lastfm(){

  document.getElementById('button_next').value = "lastfm";

  document.getElementById("type_choosing").classList.add('d-none');
  document.getElementById("choice_header").classList.add('d-none');

  document.getElementById("lastfm_header").classList.remove('d-none');
  document.getElementById("lastfm_container").classList.remove('d-none');

  document.getElementById("action_choosing").classList.remove("d-none");
}

async function find_user(){
  var nickname = document.getElementById('lastfm_nickname').value;
  nickname_value = nickname;

  document.getElementById("loader").classList.remove("d-none");
  const response_info = await fetch("/users/getUserLasfmInfo/?nickname=" + nickname, {
    headers: { "Accept": "application/json" }
  });
  document.getElementById("loader").classList.add("d-none");


  if (response_info.status == 404){
    document.getElementById('user_not_found').classList.remove('d-none');
    document.getElementById('lastFmNickname').reset();
    return;
  };

  var info = await response_info.json();
  var image = info["user"]["image"][3];

  var frame = document.getElementById('lastfm_pfp');
  if (image["#text"] === "") {
    frame.style.backgroundImage = "url(/static/login/img/no-profile-image.png)";
  }
  else {
    frame.style.backgroundImage = "url(" + image["#text"] + ")";
  }
  frame.classList.remove('d-none');
  button = document.getElementById("button_next").classList.remove('d-none');
}


async function apply_preferences(nickname){
  var type = document.getElementById('button_next').value;
  console.log(type);
  if (type === "genres") {
    var result = await choose_genres(nickname);
  }
  else if (type === "lastfm"){
    var lastfm_nickname = document.getElementById('lastfm_nickname').value; 
    var result = await import_tracks(nickname,  lastfm_nickname);
  }
  else{
    alert("WRONG REG TYPE");
  }
  console.log(result);
  if (result === true){

    document.cookie = `reg_nickname=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`
    window.location.replace('/login');
  }
}


async function choose_genres(nickname) {

  console.log(nickname)
  var genres = {
    "hip hop"     : document.getElementById('CB_hiphop').checked,
    "rock"        : document.getElementById('CB_rock').checked,
    "rap"         : document.getElementById('CB_rap').checked,
    "pop"         : document.getElementById('CB_pop').checked,
    "alternative" : document.getElementById('CB_alt').checked,
    "classic"   : document.getElementById('CB_class').checked,
    "edm"         : document.getElementById('CB_edm').checked
  }
  
  console.log(genres);
  // return false;

  // SetUserGenres
  
  const response = await fetch("/music/setFavouriteGenres/", {
  method: "POST",
  headers: { "Accept": "application/json" },
  body: JSON.stringify({
    nickname : nickname,
    genres : genres
    })
  });

  
  if (response.ok === true) {
    return true;
  }
  else {alert('Genres error!'); return false;};
}



async function import_tracks(nickname, lastFmNickname) {

  // console.log(nickname);
  // console.log(lastFmNickname);


  // const response_set_lastfm = await fetch("/users/setUserLasfmNickname", {
  //   method: "POST",
  //   headers: { "Accept": "application/json" },
  //   body: JSON.stringify({
  //     nickname : nickname,
  //     lastfm_nickname : lastFmNickname
  //     })
  // });

  // console.log(response_set_lastfm);

  document.getElementById("loader").classList.remove("d-none");
  const response_integrate = await fetch("/music/lastFM-integration/", {
  method: "POST",
  headers: { "Accept": "application/json" },
  body: JSON.stringify({
    nickname : nickname,
    lastFmNickname : lastFmNickname
    })
  });
  document.getElementById("loader").classList.add("d-none");
  console.log(response_integrate);
  // return false;

  if (response_integrate.ok === true){
    return true;
  }
  else{
    return false;
  }

  // if (response_integrate.status == 400)

}