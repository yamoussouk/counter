$(document).ready(function(){
		if(getCookie("HideCookie") != "true") {
			$("#cookie-consent").css('display','block');
		}
	});

	function SetCookieAndHideDiv(){
		Cookies.set('HideCookie','true', { expires: 1 });
		$("#cookie-consent").css('display','none');
	}

	function getCookie(cname) {
		var name = cname + "=";
		var ca = document.cookie.split(';');

		for(var i=0; i<ca.length; i++) {
			var c = ca[i];
			while (c.charAt(0)==' ') c = c.substring(1);
			if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
		}

		return "";
	}
