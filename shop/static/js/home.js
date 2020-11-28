$('.home-collection-item').on('mouseenter', function(e) {
    $(this).find('img').css('opacity', '1');
});

$('.home-collection-item').on('mouseleave', function(e) {
    $(this).find('img').css('opacity', '.3');
});
