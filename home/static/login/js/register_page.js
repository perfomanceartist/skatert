function hash(string) {
    const utf8 = new TextEncoder().encode(string);
    return crypto.subtle.digest('SHA-256', utf8).then((hashBuffer) => {
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray
        .map((bytes) => bytes.toString(16).padStart(2, '0'))
        .join('');
      return hashHex;
    });
  }

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
    
    var passwordHash = await hash(password);
    console.log(passwordHash);
    const response = await fetch("/api/register", {
        method: "POST",
        headers: { "Accept": "application/json" },
        body: JSON.stringify({
            nickname: nickname,
            email: email,
            hash: passwordHash
        })
    });
    var responseJson = await response.json();
    var status = responseJson['error']['code'];

    if (status == 222) {  // nickname is not unique
        document.getElementById('nickname_duplicate').classList.remove('d-none');
        document.getElementById('nickname').reset();
        return;
    }
    if (status == 223) {  // empty field(s)
        document.getElementById('empty_field').classList.remove('d-none');
        return;
    }
    if (status == 225) {  // email format
        document.getElementById('incorrect_email').classList.remove('d-none');
        document.getElementById('email').reset();
        return;
    }
    if (response.ok === true || status == 0) {
        document.cookie = `reg_nickname=${nickname};`;
        window.location.replace('/genres');
    }
    else alert('Registration error!');
}