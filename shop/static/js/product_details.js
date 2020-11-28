$('.minus').on('click', function(e) {
    var val = $(this).next().next().val();
    if (val > 1) {
        $(this).next().next().val(val-1);
    }
});

$('.plus').on('click', function(e) {
    var val = $(this).prevAll('#id_quantity').val();
    product_type = $('.product-wrapper').attr('class')
    if (product_type.split(' ')[0] == 'multi-product') {
        var max = $('#id_quantity').attr('max')
        if (val < max) {
            $(this).prevAll('#id_quantity').val(parseInt(val)+1);
        }
    } else {
        var stock = $('.product-wrapper').attr('data-stock')
        if (val < stock) {
            $(this).prevAll('#id_quantity').val(parseInt(val)+1);
        }
    }
});

$('document').ready(function(){
    var stock = $('.product-attributes-color select').find(":selected").attr('data-stock')
    if (stock === undefined) {
        stock = $('.product-wrapper').attr('data-stock')
    }
    $('#id_quantity').attr('max', stock)
    var color = $('.product-attributes-color select').find(":selected").text()
    if (color != '') {
        $('#id_color').val(color)
    }
    var val = $('input[type="radio"][name="stud"]:checked').val()
    $('#id_stud').val(val)
});

$('.product-attributes-color select').change(function(e){
    var stock = $(this).find(":selected").attr('data-stock')
    $('#id_quantity').attr('max', stock)
    $('#id_quantity').val(1)
    var source = $(this).find(":selected").attr('data-img-src')
    $('.product-image img.product_image').attr('src', source)
    var color = $(this).find(":selected").text()
    $('#id_color').val(color)
    $('.product-thumbnail.selected').removeClass('selected')
    $('.product-thumbnail img[data-name="' + color + '"]').parent().addClass('selected')
});

$('.product-thumbnail img').on('click', function(e) {
    $('.product-thumbnail.selected').removeClass('selected');
    $(this).parent().addClass('selected');
    var source = $(this).attr('src')
    $('.product-image img.product_image').attr('src', source)
});

$('input[type="radio"][name="stud"]').on('change', function(e) {
    var val = $('input[type="radio"][name="stud"]:checked').val()
    $('#id_stud').val(val)
});

$('document').ready(function(){
    if($('#errorModal .modal-body .messages').length > 0) {
        $('#error_button').click();
    }
});

$('#detail-page-filter-button').click(function(e) {
    $(this).next().toggleClass('opened')
    $(this).toggleClass('closed')
});

$('#mobile-filter-close').click(function(e) {
    $(this).parent().toggleClass('opened')
    $('#detail-page-filter-button').toggleClass('closed')
});

