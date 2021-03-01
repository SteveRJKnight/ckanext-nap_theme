function setUrl(fromField, toField) {
  const fromValue = document.getElementById(fromField).value.replace(/ /g, '-');
  const toObj = document.getElementById(toField);
  const uniqueString = Date.now().toString(16);
  toObj.value = `${fromValue}-${uniqueString}`.toLowerCase();
}

function setCookie(name, value) {
  document.cookie = `${name}=${value}; path=/; max-age=31536000`;
}

function eraseCookie(name) {   
  document.cookie = `${name}=; path=/; max-age=-99999999;`;  
}
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

function setCookieMessageVisibility(cookie, state) {
  const link = document.getElementById(cookie);
  link.style.display = state;
}

function showLongCookieMessage() {
  setCookieMessageVisibility('global-cookie-message', 'block');
  setCookieMessageVisibility('global-cookie-message-long', 'block');
  setCookieMessageVisibility('global-cookie-message-short', 'none'); 
}

function showShortCookieMessage() {
  setCookieMessageVisibility('global-cookie-message', 'block');
  setCookieMessageVisibility('global-cookie-message-long', 'none');
  setCookieMessageVisibility('global-cookie-message-short', 'block');
}

function hideShortCookieMessage() {
  setCookieMessageVisibility('global-cookie-message-short', 'none');
  setCookie('hide_cookie_policy','hide');
}

function saveCookieChoice() {
  const currentCookieState = document.getElementById('cookies-analytics-yes').checked;
  setCookie('cookie_policy', currentCookieState ? 'yes' : 'no'); 
  location.replace(document.referrer);
}

function setupCookies() {
  const cookiePolicyFound = getCookie('cookie_policy');
  const hideCookiePolicyFound = getCookie('hide_cookie_policy');
  if (cookiePolicyFound) {
      if (hideCookiePolicyFound) {
        // do nothing
      } else {
        showShortCookieMessage();
      }
      let radioBtn
      if (cookiePolicyFound === 'yes' ) {
        radioBtn = document.getElementById("cookies-analytics-yes");
      } else if (cookiePolicyFound === 'no') {
        radioBtn = document.getElementById("cookies-analytics-no");
      }
      if (radioBtn) {
        radioBtn.checked = true;
      }

  } else {
    showLongCookieMessage();
  }
}

function setGoogleAnalyticsScript(){
  const script = document.createElement('script');
  script.type = 'text/javascript';
  script.src = 'https://www.googletagmanager.com/gtag/js?id=G-0LCLXB2HEZ';
  document.head.appendChild(script);
  script.src = 'https://www.googletagmanager.com/gtm.js?id=GTM-TQDBGHF';
  document.head.appendChild(script);
}

function setupGoogleAnalytics(){
  const cookiePolicyValue = getCookie('cookie_policy');
  if (cookiePolicyValue === 'yes') {
    window['ga-disable-G-0LCLXB2HEZ'] = false;
    setGoogleAnalyticsScript();
  } else {
    window['ga-disable-G-0LCLXB2HEZ'] = true;
    eraseCookie("_ga_0LCLXB2HEZ");
    eraseCookie("_ga");
  }
}

this.GOVUKFrontend.initAll()
document.body.className = ((document.body.className) ? document.body.className + ' js-enabled' : 'js-enabled')
setupCookies();
setupGoogleAnalytics();
