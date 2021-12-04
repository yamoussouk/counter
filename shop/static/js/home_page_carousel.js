$(window).on('load',function() {
    var a = $("#owl-home-carousel");
    var b = $("#owl-products-carousel");
    b.owlCarousel({
        stagePadding: 50,
        loop: !0,
        margin: 30,
        lazyLoad: !0,
        nav: !0,
        dots: !1,
        autoplay: !0,
        autoplayTimeout: 3e3,
        autoplayHoverPause: !1,
        navText: ['<i class="fa fa-angle-left" aria-hidden="true"></i>', '<i class="fa fa-angle-right" aria-hidden="true"></i>'],
        responsive: { 0: { items: 1 }, 600: { items: 2 }, 1025: { items: 4 } }
    });
    a.owlCarousel({
        loop: true,
        margin: 30,
        lazyLoad: true,
        nav: false,
        dots: true,
        autoplay: true,
        autoplayTimeout: 3e3,
        autoplayHoverPause: true,
        animateOut: "fadeOut",
        responsive: { 0: { items: 1 }, 600: { items: 1 }, 1025: { items: 1 } } })
});
