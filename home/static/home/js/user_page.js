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
  console.log(nickname)


  // const response = await fetch("/api/integrate", {
  //     method: "POST",
  //     headers: { "Accept": "application/json" },
  //     body: JSON.stringify({
  //         nickname: nickname
  //     })
  // });

  // console.log(response)

}