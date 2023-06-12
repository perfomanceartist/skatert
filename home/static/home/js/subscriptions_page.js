async function unsubscribe_handler(button, nickname){
  console.log(nickname);
// console.log(button.value);

  var target_nickname = button.closest(".list_element").querySelector(".subscribtion_name").innerText;
  console.log(target_nickname)

  const response = await fetch("/users/subscribe", {
    method: "POST",
    headers: { "Accept": "application/json" },
    body: JSON.stringify({
        nickname : nickname,
        target_nickname: target_nickname,
        subscribed: false
    })
    });

    console.log(response.status);

    setup_subscriptions_page(nickname);
}

async function set_listeners(nickname){
  var buttons = document.querySelectorAll('.btn-unsub');

  for (var i = 0; i < buttons.length; i++) {
    buttons[i].addEventListener("click", (function(button) {
      return function() {
        unsubscribe_handler(button, nickname);
      }
    })(buttons[i]));
  }
}

async function setup_subscriptions_page(nickname){
  document.getElementById("user_subscriptions").innerHTML = "";
  document.getElementById("subscriptions_search_field").value = "";

  console.log(nickname)

  const links = document.getElementsByClassName("nav-item");
  for (var i in links){
    var link = links[i];
    try {
      link.style.display = "none";
    } catch (error) {}
  }

  console.log("LIST_USER_SUBSCRIPTIONS");
  const response_subscriptions = await fetch("users/subscriptions?nickname=" + nickname, {
    headers: { "Accept": "application/json" }
  });

  const subs = await response_subscriptions.json();
  // console.log(subs)
  for (var i in subs) {
    var sub = subs[i];
    var element = document.createElement("div");
    element.className = "list_element";

    var subscribtion_name = document.createElement("li");
    subscribtion_name.className = "subscribtion_name";
    subscribtion_name.innerText = sub;

    var button_unsub = document.createElement("button");
    button_unsub.className = "btn-primary btn-unsub";
    button_unsub.innerText = "Отписаться";

    element.appendChild(subscribtion_name);
    element.appendChild(button_unsub);
    document.getElementById("user_subscriptions").appendChild(element);
  }
  
  set_listeners(nickname);
}

async function subscribe_to_user(nickname) {

  document.getElementById("user_not_found").classList.add('d-none');
  document.getElementById("already_subscribed").classList.add('d-none');
  
  var target_nickname = document.getElementById("subscriptions_search_field").value;

  const response = await fetch("/users/subscribe", {
    method: "POST",
    headers: { "Accept": "application/json" },
    body: JSON.stringify({
        nickname : nickname,
        target_nickname: target_nickname,
        subscribed: true
    })
    });
    if (response.ok === true) {
      setup_subscriptions_page(nickname)
    }
    else if (response.status == 400) {
      document.getElementById("already_subscribed").classList.remove('d-none');
    }
    else if (response.status == 500) {
      document.getElementById("user_not_found").classList.remove('d-none');
    }
  
  
  }