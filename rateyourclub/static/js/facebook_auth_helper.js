var regex = /\/#([^#]*[code|token|expires_in])/
if (window.location.href.match(regex)){
  window.location = window.location.href.replace(regex,"?$1")
} else {
  window.location = document.getElementById("login_url").href
}
