function SetCookieAndHideDiv(){Cookies.set("HideCookie","true",{expires:1}),$("#cookie-consent").css("display","none")}function SetInfoAndHideDiv(){Cookies.set("HideInfo","true",{expires:1}),$("#information-consent").css("display","none")}function getCookie(e){for(var o=e+"=",n=document.cookie.split(";"),i=0;i<n.length;i++){for(var t=n[i];" "==t.charAt(0);)t=t.substring(1);if(0==t.indexOf(o))return t.substring(o.length,t.length)}return""}$(document).ready(function(){"true"!=getCookie("HideCookie")&&$("#cookie-consent").css("display","block"),"true"!=getCookie("HideInfo")&&$("#information-consent").css("display","block")});