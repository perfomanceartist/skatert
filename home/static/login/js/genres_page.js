async function choose_genres(nickname) {

  console.log(nickname)

  // var hh = document.getElementById('CB_hiphop').checked;
  // var rap = document.getElementById('CB_rap').checked;

  var genres = {
    "hip hop"     : document.getElementById('CB_hiphop').checked,
    "rock"        : document.getElementById('CB_rock').checked,
    "rap"         : document.getElementById('CB_rap').checked,
    "pop"         : document.getElementById('CB_pop').checked,
    "alternative" : document.getElementById('CB_alt').checked,
    "edm"         : document.getElementById('CB_edm').checked,
    "classical"   : document.getElementById('CB_class').checked
  }
  

  // SetUserGenres
  
  const response = await fetch("/music/setFavouriteGenres/", {
  method: "POST",
  headers: { "Accept": "application/json" },
  body: JSON.stringify({
    nickname : nickname,
    genres : genres
    })
  });

  console.log(response)
  if (response.ok === true) {
    document.cookie = `reg_nickname=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`
    window.location.replace('/login');
  }
  else alert('Genres error!');
}
 