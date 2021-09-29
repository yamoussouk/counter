var modes = { 0: "Személyes átvétel", 1: "Csomagkuldo", 2: "FoxPost", 3: "Házhozszállítás", 4: "Ajanlott" };
var packetaApiKey = $("meta[name=cs_a]").attr("content");
var foxpostID = '#id_fox_post'
var csomagkuldoID = '#id_csomagkuldo'
var delivery_type = 0

$("document").ready(function () {
    // coupon - gift card button collapses
    $('#collapseCoupon').on('show.bs.collapse', function () {
      if (!$('button[aria-controls="collapseGift"]').hasClass("collapsed")) {
            $("#collapseGift").collapse('hide');
        }
    }),
    $('#collapseGift').on('show.bs.collapse', function () {
      if (!$('button[aria-controls="collapseCoupon"]').hasClass("collapsed")) {
            $("#collapseCoupon").collapse('hide');
        }
    }),
    $("#errorModal .modal-body .messages").length > 0 && $("#error_button").click();
    if (localStorage.getItem("cart")) {
        fill_info_from_local_storage()
    } else set_delivery_type(0);
    if ($("#collapseTwo").hasClass("show")) {
        set_total_price(get_fox_post_price() + get_total_price());
    } else
        l = get_total_price();
        if ($("#collapseThree").hasClass("show")) {
            set_total_price(get_delivery_price() + l);
        }
        if ($("#collapseFour").hasClass("show")) {
            inlineFullHU();
            set_total_price(get_csomagkuldo_price() + l);
        }
        if ($("#collapseFive").hasClass("show")) {
            set_total_price(get_envelope_price() + l);
        }
})
$("#personal button").on("click", function (e) {
    $("#collapseOne input").attr("required", "true").val(""),
    resetFoxPost(),
    removeDeliveryRequired(),
    resetCsomagkuldo(),
    set_delivery_type(0),
    removeDeliveryRequired(),
    resetDeliverySafe(),
    set_total_price(get_total_price());
})
$("#delivery button").on("click", function (e) {
    $("#collapseThree input:not(#d_note)").attr("required", "true").val(""),
    resetFoxPost(),
    resetPersonal(),
    resetCsomagkuldo(),
    set_delivery_type(3);
    set_total_price(get_delivery_price() + get_total_price());
    resetDeliverySafe()
})
$("#envelope button").on("click", function (e) {
    $("#collapseFive input:not(#d_note)").attr("required", "true").val(""),
    resetFoxPost(),
    resetPersonal(),
    removeDeliveryRequired(),
    removeDeliveryRequired(),
    resetCsomagkuldo(),
    set_delivery_type(4);
    set_total_price(get_envelope_price() + get_total_price());
    resetDeliverySafe()
})
$("#delivery-form").one("submit", function (e) {
    var a = {};
    a.full_name = $("#full_name").val(),
    a.email = $("#email_address").val(),
    a.phone = $("#phone_number").val(),
    a.billing_address = $("#billing_address").val(),
    a.billing_postal_code = $("#billing_postal_code").val(),
    a.billing_city = $("#billing_city").val(),
    a.product_note = $("#product_note").val(),
    a.delivery_type = delivery_type,
    a.timestamp = new Date().getTime();
    if ($("#first_name").val() != '') {
        a.csomagkuldo = "", a.fox_post = "", a.delivery_name = "", a.address = "", a.postal_code = "", a.city = "", a.note = "", a.first_name = $("#first_name").val(), a.last_name = $("#last_name").val()
    } else if ($("#collapseFive #delivery_full_name").val() != '') {
        a.csomagkuldo = "";
        a.fox_post = "";
        a.first_name = "";
        a.last_name = "";
        address = $("#collapseFive #d_address").val(), postal_code = $("#collapseFive #d_zip").val(), city = $("#collapseFive #d_city").val(),
        delivery_name = $("#collapseFive #delivery_full_name").val(), note = $("#collapseFive #d_note").val(),
        a.delivery_name = delivery_name, a.address = address, a.postal_code = postal_code, a.city = city, a.note = note,
        $('input[name="address"]').val(address), $('input[name="delivery_name"]').val(delivery_name),
        $('input[name="postal_code"]').val(postal_code), $('input[name="city"]').val(city), $('input[name="note"]').val(note)
    } else if ($("#collapseThree #delivery_full_name").val() != '') {
        a.csomagkuldo = "";
        a.fox_post = "";
        a.first_name = "";
        a.last_name = "";
        address = $("#collapseThree #d_address").val(), postal_code = $("#collapseThree #d_zip").val(), city = $("#collapseThree #d_city").val(),
        delivery_name = $("#collapseThree #delivery_full_name").val(), note = $("#collapseThree #d_note").val(),
        a.delivery_name = delivery_name, a.address = address, a.postal_code = postal_code, a.city = city, a.note = note,
        $('input[name="address"]').val(address), $('input[name="delivery_name"]').val(delivery_name),
        $('input[name="postal_code"]').val(postal_code), $('input[name="city"]').val(city), $('input[name="note"]').val(note)
    } else if ($(foxpostID).val() != '') {
        a.csomagkuldo = "", a.fox_post = $(foxpostID).val(), a.delivery_name = "", a.address = "", a.postal_code = "", a.city = "", a.note = "", a.first_name = "", a.last_name = ""
    } else if ($(csomagkuldoID).val() != '') {
        a.csomagkuldo = $(csomagkuldoID).val(), a.fox_post = "", a.delivery_name = "", a.address = "", a.postal_code = "", a.city = "", a.note = "", a.first_name = "", a.last_name = ""
    }
    window.removeEventListener("message", receiveMessage, !1),
    localStorage.setItem("cart", JSON.stringify(a)),
    set_delivery_type(delivery_type)
    $(this).submit();
})
window.addEventListener("message", receiveMessage, !1);
function showSelectedPickupPoint(e) {
    var a = document.getElementById("csomagkuldo-body");
    $("#collapseFour").removeClass("show"), (a.style.height = "0px");
    var l = e ? e.name : "None";
    if (localStorage.getItem("cart")) {
        var cart = JSON.parse(localStorage.getItem("cart"));
        cart.csomagkuldo = l
        localStorage.setItem("cart", JSON.stringify(cart))
    }
    $(csomagkuldoID).val(l),
    set_delivery_type(1),
    resetPersonal(),
    resetFoxPost(),
    removeDeliveryRequired(),
    resetPersonal(),
    resetDeliverySafe(),
    removeDeliveryRequired(),
    set_total_price(get_csomagkuldo_price() + get_total_price());
    "None" !== l &&
        ($("body").prepend(
            '<div id="modal-wrapper"><div id="modal-body"><p>A következő automatát választottad: ' + l + '</p><div class="modal-button-wrapper"><button class="modal-close" onClick="close_modal()">Bezár</button></div></div></div>'
        ),
        $("body").prepend('<div id="foxpost-modal-backdrop" />'));
}
function removeDeliveryRequired() {
    $("#delivery_full_name").removeAttr("required").val(""), $("#d_address").removeAttr("required").val(""), $("#d_zip").removeAttr("required").val(""), $("#d_city").removeAttr("required").val("");
}

function resetCsomagkuldo() {
    $(csomagkuldoID).val("");
}

function resetFoxPost() {
    $(foxpostID).val("");
}

function resetPersonal() {
    $("#collapseOne input").removeAttr("required").val("");
}

function set_delivery_type(type) {
    $("#id_delivery_type").val(type);
    delivery_type = type;
}

function resetDeliverySafe() {
    $("#delivery_safe").val("");
}

function set_total_price(price) {
    $("#total_price").text(price + " Ft");
}

function get_total_price() {
    return parseInt($("#total_price").attr("data-price"));
}

function clear() {
    for (var e = document.querySelectorAll(".method-detail"), a = 0; a < e.length; a++) (e[a].innerText = ""), (e[a].style.height = "0");
    Packeta.Widget.close();
}

function inlineFullHU() {
    var e = document.getElementById("csomagkuldo-body");
    clear(), (e.style.height = "600px"), Packeta.Widget.pick(packetaApiKey, showSelectedPickupPoint.bind(e), { country: "hu", language: "hu" }, e);
}

function receiveMessage(e) {
    if ("https://cdn.foxpost.hu" == e.origin) {
        var a = JSON.parse(e.data);
        $(foxpostID).val(a.name + ";" + a.address),
        set_delivery_type(2),
        resetPersonal(),
        resetDeliverySafe(),
        resetCsomagkuldo(),
        removeDeliveryRequired();
        set_total_price(get_fox_post_price() + get_total_price()),
            void 0 !== a.name &&
                ($("body").prepend(
                    '<div id="modal-wrapper"><div id="modal-body"><p>A következő automatát választottad: ' +
                        a.name +
                        '</p><div class="modal-button-wrapper"><button class="modal-close" onClick="close_modal()">Bezár</button></div></div></div>'
                ),
                $("body").prepend('<div id="foxpost-modal-backdrop" />'));
    } else {
        resetPersonal(), removeDeliveryRequired(), resetFoxPost();
    }
}

function close_modal() {
    $("#modal-wrapper").remove(), $("#foxpost-modal-backdrop").remove();
}

function show_collapse(collapse) {
    $(collapse).addClass("show");
}

function hide_collapse(collapse) {
    $(collapse).removeClass("show");
}

function get_fox_post_price() {
    return parseInt($("#fox_price").text());
}

function get_envelope_price() {
    return parseInt($("#envelope_price").text());
}

function get_csomagkuldo_price() {
    return parseInt($("#csomagkuldo_price").text());
}

function get_delivery_price() {
    return parseInt($("#delivery_price").text());
}

function fill_info_from_local_storage() {
    var e = JSON.parse(localStorage.getItem("cart"));
    $("#full_name").val(e.full_name),
    $("#email_address").val(e.email),
    $("#phone_number").val(e.phone),
    $("#billing_address").val(e.billing_address),
    $("#billing_postal_code").val(e.billing_postal_code),
    $("#billing_city").val(e.billing_city),
    $("#product_note").val(e.product_note),
    set_delivery_type(e.delivery_type),
    removeDeliveryRequired(),
    "0" == e.delivery_type
        ? ($("#personal h5 button").attr("aria-expanded", "true").addClass("collapsed"),
          $("#collapseOne").addClass("show"),
          $("#first_name").val(e.first_name).attr("required", "required"),
          $("#last_name").val(e.last_name).attr("required", "required"))
        : "1" == e.delivery_type
        ? ($("#csomagkuldo h5 button").attr("aria-expanded", "true").addClass("collapsed"), show_collapse("#collapseFour"), hide_collapse("#collapseOne"), resetPersonal(), resetFoxPost(), removeDeliveryRequired(),
        $("#id_csomagkuldo").val(e.csomagkuldo))
        : "2" == e.delivery_type
        ? ($("#foxt-post h5 button").attr("aria-expanded", "true").addClass("collapsed"), show_collapse("#collapseTwo"), hide_collapse("#collapseOne"), resetPersonal(), resetCsomagkuldo(), removeDeliveryRequired(),
        $("#id_fox_post").val(e.fox_post))
        : "3" == e.delivery_type
        ? ($("#delivery h5 button").attr("aria-expanded", "true").addClass("collapsed"), show_collapse("#collapseThree"), hide_collapse("#collapseOne"), resetPersonal(), resetFoxPost(), resetCsomagkuldo(),
        $("#collapseThree #delivery_full_name").val(e.delivery_name), $("#collapseThree #d_address").val(e.address),
        $("#collapseThree #d_zip").val(e.postal_code), $("#collapseThree #d_city").val(e.city), $("#collapseThree #d_note").val(e.note))
        : "4" == e.delivery_type && ($("#envelope h5 button").attr("aria-expanded", "true").addClass("collapsed"), show_collapse("#collapseFive"), hide_collapse("#collapseOne"), resetPersonal(), resetFoxPost(), resetCsomagkuldo(),
        $("#collapseFive #delivery_full_name").val(e.delivery_name), $("#collapseFive #d_address").val(e.address),
        $("#collapseFive #d_zip").val(e.postal_code), $("#collapseFive #d_city").val(e.city), $("#collapseFive #d_note").val(e.note));
    }
