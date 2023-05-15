var step = 1;
var userNickname = '';
  async function authStep1() {
    console.log('auth/step1');
    var nickname = document.getElementById('loginControlInputNick').value;
    var password = document.getElementById('loginControlPassword').value;
    
    const response = await fetch("/api/login_pass", {
      method: "POST",
      headers: { "Accept": "application/json" },
      body: JSON.stringify({
        nickname: nickname,
        hash: password
      })
    });
    
    if (response.status == 224) {  // unknown user
      document.getElementById('unknown_user').classList.remove('d-none');
      return false;
    }
    if (response.status == 223) {  // empty_field(s)
      document.getElementById('empty_field').classList.remove('d-none');
      return false;
    }
    if (response.status == 201) {
      var responseJson = response.json();
      document.cookie += `nickname=${userNickname}; token=${responseJson['token']}`;
      window.location.replace('/');
      return [true, false];
    }
    if (response.ok === true) {
      userNickname = nickname; 
      return [true, true];
    }
    else {
      document.getElementById('incorrect_pass').classList.remove('d-none');
      document.getElementById('password').reset();
      return [false, false];
    }
  }


  async function authStep2() {
    var code = document.getElementById('loginControlCode').value;
    
    const response = await fetch("/api/login_email", {
      method: "POST",
      headers: { "Accept": "application/json" },
      body: JSON.stringify({
        nickname: userNickname,
        code: code
      })
    });
    
    if (response.ok === true) {
      var responseJson = await response.json();
      document.cookie += `nickname=${userNickname}; token=${responseJson['token']}`;
      window.location.replace('/');
    }
    else {
      document.getElementById('incorrect_code').classList.remove('d-none');
      document.getElementById('email_code').reset();
    }
  }


  async function auth() {
    document.getElementById('unknown_user').classList.add('d-none');
    document.getElementById('empty_field').classList.add('d-none');
    document.getElementById('incorrect_pass').classList.add('d-none');
    document.getElementById('incorrect_code').classList.add('d-none');
    if (step == 1) {
      var response = await authStep1();
      var result = response[0];
      var is_email = response[1];
      
      if (result === true) {
        step = 2;
        if (is_email === true) {
          document.getElementById('div-email-code').classList.remove('d-none');
        }
      }
    }
    else {
      await authStep2();
    }
  }