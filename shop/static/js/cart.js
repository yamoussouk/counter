/* cart */

$('document').ready(function(){
    if ($('#collapseTwo').hasClass('show')) {
        var price = $('#fox_price').text()
        var total_price = $('#total_price').attr('data-price')
        var new_price = parseInt(price) + parseInt(total_price)
        $('#total_price').text(new_price + ' Ft')
    } else if ($('#collapseThree').hasClass('show')) {
        var price = $('#delivery_price').text()
        var total_price = $('#total_price').attr('data-price')
        var new_price = parseInt(price) + parseInt(total_price)
        $('#total_price').text(new_price + ' Ft')
    } else if ($('#collapseFour').hasClass('show')) {
        inlineFullHU()
        var price = $('#csomagkuldo_price').text()
        var total_price = $('#total_price').attr('data-price')
        var new_price = parseInt(price) + parseInt(total_price)
        $('#total_price').text(new_price + ' Ft')
    }
});

$('#foxt-post button').on('click', function(e) {
    $('#collapseOne input').removeAttr('required').val('')
    $('#id_delivery_name').val('')
    $('#id_address').val('')
    $('#id_postal_code').val('')
    $('#id_city').val('')
    $('#id_note').val('')
    $('#id_firstname').val('')
    $('#id_lastname').val('')
    $('#delivery_full_name').val('')
    $('#d_address').val('')
    $('#d_zip').val('')
    $('#d_city').val('')
    $('#d_note').val('')
    $('#first_name').val('')
    $('#last_name').val('')
    $('#delivery_safe').val('')
    var price = $('#fox_price').text()
    var total_price = $('#total_price').attr('data-price')
    var new_price = parseInt(price) + parseInt(total_price)
    $('#total_price').text(new_price + ' Ft')
});

$('#csomagkuldo button').on('click', function(e) {
    $('#collapseOne input').removeAttr('required').val('')
    $('#id_fox_post').val('')
    $('#id_delivery_name').val('')
    $('#id_address').val('')
    $('#id_postal_code').val('')
    $('#id_city').val('')
    $('#id_note').val('')
    $('#id_firstname').val('')
    $('#id_lastname').val('')
    $('#delivery_full_name').val('')
    $('#d_address').val('')
    $('#d_zip').val('')
    $('#d_city').val('')
    $('#d_note').val('')
    $('#first_name').val('')
    $('#last_name').val('')
    $('#delivery_safe').val('')
    var price = $('#csomagkuldo_price').text()
    var total_price = $('#total_price').attr('data-price')
    var new_price = parseInt(price) + parseInt(total_price)
    $('#total_price').text(new_price + ' Ft')
});

$('#personal button').on('click', function(e) {
    $('#collapseOne input').attr('required', 'true').val('')
    $('#id_fox_post').val('')
    $('#id_delivery_name').val('')
    $('#id_address').val('')
    $('#id_postal_code').val('')
    $('#id_city').val('')
    $('#id_note').val('')
    $('#delivery_full_name').val('')
    $('#d_address').val('')
    $('#d_zip').val('')
    $('#d_city').val('')
    $('#d_note').val('')
    $('#delivery_safe').val('')
    var total_price = $('#total_price').attr('data-price')
    $('#total_price').text(total_price + ' Ft')
});

$('#delivery button').on('click', function(e) {
    $('#collapseOne input').removeAttr('required').val('')
    $('#collapseThree input:not(#d_note)').attr('required', 'true').val('')
    $('#id_fox_post').val('')
    $('#id_firstname').val('')
    $('#id_lastname').val('')
    $('#first_name').val('')
    $('#last_name').val('')
    $('#delivery_safe').val('')
    var price = $('#delivery_price').text()
    var total_price = $('#total_price').attr('data-price')
    var new_price = parseInt(price) + parseInt(total_price)
    $('#total_price').text(new_price + ' Ft')
});

$('#delivery-form').one('submit', function(e) {
//    e.preventDefault();
    var validationFailure = false

    var val = $('#full_name').val()
    $('#id_fullname').val(val)
    val = $('#email_address').val()
    $('#id_email').val(val)
    val = $('#phone_number').val()
    $('#id_phone').val(val)
    val = $('#first_name').val()
    if (val !== undefined && val != '') {
        $('#id_firstname').val(val)
        $('#id_delivery_type').val('Személyes átvétel')
    }
    val = $('#last_name').val()
    if (val !== undefined && val != '') {
        $('#id_lastname').val(val)
    }
    val = $('#delivery_full_name').val()
    if (val !== undefined && val != '') {
        $('#id_delivery_name').val(val)
        $('#id_delivery_type').val('Házhozszállítás')
    }
    val = $('#d_address').val()
    if (val !== undefined) {
        $('#id_address').val(val)
    }
    val = $('#d_zip').val()
    if (val !== undefined) {
        $('#id_postal_code').val(val)
    }
    val = $('#d_city').val()
    if (val !== undefined) {
        $('#id_city').val(val)
    }
    val = $('#d_note').val()
    if (val !== undefined) {
        $('#id_note').val(val)
    }
    val = $('#id_delivery_type').val()
    if (val === undefined || val == '') {
        var temp = $('#delivery_safe').val();
        if (temp.split(';')[0] == 'cs') {
            $('#id_delivery_type').val('Csomagkuldo')
            $('#id_csomagkuldo').val(temp.split(';').slice(1));
        } else if (temp.split(';')[0] == 'fp') {
            $('#id_delivery_type').val('FoxPost')
            $('#id_fox_post').val(temp.split(';').slice(1));
        }
    }
    window.removeEventListener('message', receiveMessage, false);
    $(this).submit();
});

function receiveMessage(event) {
    if (event.origin == 'https://cdn.foxpost.hu') {
        var apt = JSON.parse(event.data);
        $('#id_fox_post').val(apt.name + ';' + apt['address'])
        $('#id_delivery_type').val('FoxPost')
        if (apt.name !== undefined) {
            $('body').prepend('<div id="modal-wrapper">' +
                '<div id="modal-body"><p>A következő automatát választottad: ' + apt.name + '</p>' +
                    '<div class="modal-button-wrapper"><button class="modal-close" onClick="close_modal()">Bezár</button></div>' +
                '</div>' +
             '</div>')
             $('body').prepend('<div id="foxpost-modal-backdrop" />')
        }
    }
}

window.addEventListener('message', receiveMessage, false);

function close_modal() {
    $('#modal-wrapper').remove();
    $('#foxpost-modal-backdrop').remove();
}

$('document').ready(function(){
    if($('#errorModal .modal-body .messages').length > 0) {
        $('#error_button').click();
    }
});

var packetaApiKey = $('meta[name=cs_a]').attr('content')

function clear()
{
    var elements = document.querySelectorAll('.method-detail');
    for(var i = 0; i < elements.length; i++) {
        elements[i].innerText = "";
        elements[i].style.height = "0";
    }
    Packeta.Widget.close();
}

function inlineFullHU()
{
    var div = document.getElementById('csomagkuldo-body');
    clear();
    div.style.height = "600px";

    Packeta.Widget.pick(
        packetaApiKey,
        showSelectedPickupPoint.bind(div),
        {country: 'hu', language: 'hu'},
        div
    );
}

function showSelectedPickupPoint(point)
{
    var div = document.getElementById('csomagkuldo-body');
    $('#collapseFour').removeClass('show')
    div.style.height = "0px";
    var p = (point ? point.name : "None")
    $('#id_csomagkuldo').val(p)
    $('#id_delivery_type').val('Csomagkuldo')
    if (p !== "None") {
        $('body').prepend('<div id="modal-wrapper">' +
            '<div id="modal-body"><p>A következő automatát választottad: ' + p + '</p>' +
                '<div class="modal-button-wrapper"><button class="modal-close" onClick="close_modal()">Bezár</button></div>' +
            '</div>' +
         '</div>')
         $('body').prepend('<div id="foxpost-modal-backdrop" />')
    }
};