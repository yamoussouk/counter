function timestamp_difference(e,t){return(t-e)/36e5}if($("#menu-btn").click(function(e){e.preventDefault(),$(".mobile-menu").toggleClass("opened"),$(this).toggleClass("opened")}),$("#mobile-menu-close").click(function(e){$(this).parent().toggleClass("opened")}),localStorage.getItem("cart")){var e,t=parseInt(JSON.parse(localStorage.getItem("cart")).timestamp),r=new Date().getTime(),a=timestamp_difference(t,r);isNaN(parseFloat(a))&&localStorage.removeItem("cart"),a>24&&localStorage.removeItem("cart")}$(".search-icon-wrapper").click(function(e){$("#search-bar-wrapper").addClass("search-opened")}),$("#search-bar-close").click(function(e){$("#search-bar-wrapper").removeClass("search-opened")});
