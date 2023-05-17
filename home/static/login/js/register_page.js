async function register() {
    var nickname = document.getElementById('loginControlInputNick').value;
    // var lastfm_nickname = document.getElementById('loginControlInputLastfmNick').value;
    var email = document.getElementById('loginControlInputEmail').value;
    var password = document.getElementById('loginControlInputPassword').value;
    var passwordConfirm = document.getElementById('loginControlInputPasswordConfirm').value;
    document.getElementById('nickname_duplicate').classList.add('d-none');
    document.getElementById('pass_mismatch').classList.add('d-none');
    document.getElementById('empty_field').classList.add('d-none');
    document.getElementById('incorrect_email').classList.add('d-none');

    if (passwordConfirm !== password) {
      document.getElementById('pass_mismatch').classList.remove('d-none');
      document.getElementById('password').reset();
      return;
    }
    
    
    const response = await fetch("/api/register", {
        method: "POST",
        headers: { "Accept": "application/json" },
        body: JSON.stringify({
            nickname: nickname,
            lastfm_nickname : lastfm_nickname,
            email: email,
            hash: password
        })
    });
    if (response.status == 222) {  // nickname is not unique
        document.getElementById('nickname_duplicate').classList.remove('d-none');
        document.getElementById('nickname').reset();
        return;
    }
    if (response.status == 223) {  // empty field(s)
        document.getElementById('empty_field').classList.remove('d-none');
        return;
    }
    if (response.status == 225) {  // email format
        document.getElementById('incorrect_email').classList.remove('d-none');
        document.getElementById('email').reset();
        return;
    }
    if (response.ok === true) {
        document.cookie = `reg_nickname=${nickname};`;
        window.location.replace('/genres');
    }
    else alert('Registration error!');
}