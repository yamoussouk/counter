$('#menu-btn').click(function(e){
    e.preventDefault();
    $('.mobile-menu').toggleClass('opened')
    $(this).toggleClass('opened')
});

$('#mobile-menu-close').click(function(e) {
    $(this).parent().toggleClass('opened')
});