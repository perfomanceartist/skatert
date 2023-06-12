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