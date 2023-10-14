function acceptTerms() {
  // set the magnusprotocol cookie
  setCookie();

  // redirect either to themagnusprotocolarg.com root or to the url given
  // as redirect query param
  var redirectUrl = getQueryParam('callbackUrl');

  if (redirectUrl && isValidUrl(redirectUrl)) {
    // if the terms page was visited from a different arg related domain
    // we are attaching the teramsAndConditionsAccepted=true query param
    // this parameter is checked by the aws lambda@edge of the domain
    // and if it exists the cookie is also set for that domain
    window.location.href = redirectUrl + '?termsAndConditionsAccepted=true';
  } else {
    window.location.href = '/';
  }
}

function setCookie() {
  var expires = "expires=Fri, 5 Jan 2024 23:59:59 GMT";
  document.cookie =  "themagnusprotocolargtc=true; " + expires + "; SameSite=None; Secure";
}

function getQueryParam(param) {
  var urlParams = new URLSearchParams(window.location.search);
  return urlParams.get(param);
}

function isValidUrl(string) {
  var regex = /^(http|https):\/\/[^ "]+$/;
  return regex.test(string);
}
