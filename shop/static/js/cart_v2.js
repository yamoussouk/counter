var textAreaLength=200;window.addEventListener("message",receiveMessage,!1);var modal='<div id="modal-wrapper"><div id="modal-body"><p>{0}</p><div class="modal-button-wrapper"><button class="modal-close" onClick="CloseModal()">Bez\xe1r</button></div></div></div>';function receiveMessage(b){var a=JSON.parse(b.data);"https://cdn.foxpost.hu"==b.origin&&(void 0!==a.name?($("#id_fox_post").val(a.name+";"+a.address),$(".non-foxpost").val(""),$(".non-foxpost").removeAttr("required").val(""),$("#id_delivery_type_code").val(3),SetTotalPrice("#fox_price"),modal_text="A k\xf6vetkez\u0151 automat\xe1t v\xe1lasztottad: "+a.name):modal_text="Valami hiba t\xf6rt\xe9nt a foxpost automata kiv\xe1laszt\xe1sakor, k\xe9rl\xfck pr\xf3b\xe1ld meg \xfajra a kiv\xe1laszt\xe1st!",$("body").prepend(modal.format(modal_text)),$("body").prepend('<div id="foxpost-modal-backdrop" />'))}function CloseModal(){$("#modal-wrapper").remove(),$("#foxpost-modal-backdrop").remove(),$("#collapseTwo").removeClass("show")}function clear(){for(var b=document.querySelectorAll(".method-detail"),a=0;a<b.length;a++)b[a].innerText="",b[a].style.height="0";Packeta.Widget.close()}function inlineFullHU(){var a=document.getElementById("csomagkuldo-body");clear(),a.style.height="600px",Packeta.Widget.pick(packetaApiKey,showSelectedPickupPoint.bind(a),{country:"hu",language:"hu"},a)}function showSelectedPickupPoint(c){var d=document.getElementById("csomagkuldo-body");$("#collapseFour").removeClass("show"),d.style.height="0px";var a=c?c.name:"None",b="Valami hiba t\xf6rt\xe9nt a csomagk\xfcld\u0151 pont kiv\xe1laszt\xe1sakor, k\xe9rl\xfck pr\xf3b\xe1ld meg \xfajra a kiv\xe1laszt\xe1st!";if("None"==a)return $("body").prepend(modal.format(b)),void $("body").prepend('<div id="foxpost-modal-backdrop" />');$("#id_csomagkuldo").val(a),$("#id_delivery_type_code").val(1),$(".non-csomagkuldo").removeAttr("required").val(""),SetTotalPrice("#csomagkuldo_price"),b="A k\xf6vetkez\u0151 automat\xe1t v\xe1lasztottad: "+a,$("body").prepend(modal.format(b)),$("body").prepend('<div id="foxpost-modal-backdrop" />')}function InitializeNoteCounter(a){$(a).keyup(function(b){var a=this.value.length;a>=textAreaLength?(this.value=this.value.substring(0,textAreaLength),$("#remainingC").html("0/"+textAreaLength)):$("#remainingC").html(textAreaLength-a+"/"+textAreaLength)})}function SetTotalPrice(a){var b=$(a).text(),c=$("#total_price").attr("data-price"),d=parseInt(b)+parseInt(c);$("#total_price").text(d+" Ft")}String.prototype.format=function(){for(var b=this,a=0;a<arguments.length;a++){var c=new RegExp("\\{"+a+"\\}","gi");b=b.replace(c,arguments[a])}return b},$("document").ready(function(){$("#errorModal .modal-body .messages").length>0&&$("#error_button").click();var a=$("#id_delivery_type_code").val();"0"==a?$("#collapseOne").addClass("show"):"1"==a?($("#collapseFour").addClass("show"),SetTotalPrice("#csomagkuldo_price"),inlineFullHU()):"2"==a?($("#collapseFive").addClass("show"),SetTotalPrice("#envelope_price"),$("#collapseFive input").attr("required",!0)):"3"==a?($("#collapseTwo").addClass("show"),SetTotalPrice("#fox_price")):"4"==a&&($("#collapseThree").addClass("show"),$("#collapseThree input").attr("required",!0),SetTotalPrice("#delivery_price"))}),$("#personal button").on("click",function(b){$("#id_delivery_type_code").val(0),$(".non-personal").removeAttr("required").val(""),$(".personal").attr("required","true");var a=$("#total_price").attr("data-price");$("#total_price").text(a+" Ft")}),$("#delivery button").on("click",function(a){$("#id_delivery_type_code").val(4),$(".non-delivery").removeAttr("required").val(""),$("#collapseFive input").removeAttr("required"),$("#collapseFive textarea").removeAttr("required"),$("#collapseThree input").attr("required","true"),SetTotalPrice("#delivery_price")}),$("#envelope button").on("click",function(a){$("#id_delivery_type_code").val(2),$(".non-delivery").removeAttr("required").val(""),$("#collapseThree input").removeAttr("required"),$("#collapseThree textarea").removeAttr("required"),$("#collapseFive input").attr("required","true"),SetTotalPrice("#envelope_price")}),$("#delivery-form").one("submit",function(a){"2"==$("#id_delivery_type_code").val()&&($("#collapseThree #id_delivery_name").val($("#collapseFive #id_delivery_name").val()),$("#collapseThree #id_address").val($("#collapseFive #id_address").val()),$("#collapseThree #id_address_number").val($("#collapseFive #id_address_number").val()),$("#collapseThree #id_city").val($("#collapseFive #id_city").val()),$("#collapseThree #id_postal_code").val($("#collapseFive #id_postal_code").val()),$("#collapseThree #id_note").val($("#collapseFive #id_note").val())),$(this).submit()}),packetaApiKey=$("meta[name=cs_a]").attr("content");var notes=["#product_note","#d_note","#envelope_note"];notes.forEach(a=>InitializeNoteCounter(a))