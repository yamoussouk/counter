$('.gift-card-amount select').change(function(e){
    console.log('changed')
    var price = $(this).find(":selected").val()
    $('.gift-card-price').text(price + ' Ft.-')
    $('#id_amount').val(price)
    var giftId = $(this).find(":selected").attr('data-id')
    $('.gift-card-description-wrapper form').attr('action', '/cart/add/gift/' + giftId)
});


$('document').ready(function(){
    var giftId = $('.gift-card-amount select').find(":selected").attr('data-id')
    $('.gift-card-description-wrapper form').attr('action', '/cart/add/gift/' + giftId)
});

$('document').ready(function(){
    var w_f = $('#products-wrapper .product-element:nth-child(1)').outerWidth( true );
    var w_s = $('#products-wrapper .product-element:nth-child(2)').outerWidth( true );
    var w_t = $('#products-wrapper .product-element:nth-child(3)').outerWidth( true );
    var window_width = $(window).width()
    var width = 0
    if (window_width > 1024) {
        width = w_f + w_s + w_t
    } else if (window_width > 834) {
        width = w_f + w_s
    } else {
        width = w_f
    }
    $('.pagination').width(width);
});

$('#detail-page-filter-button').click(function(e) {
    $(this).next().toggleClass('opened')
    $(this).toggleClass('closed')
});

$('#mobile-filter-close').click(function(e) {
    $(this).parent().toggleClass('opened')
    $('#detail-page-filter-button').toggleClass('closed')
});

