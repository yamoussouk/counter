$(".gift-card-amount select").change(function (t) {
    console.log("changed");
    var e = $(this).find(":selected").val();
    $(".gift-card-price").text(e + " Ft.-"), $("#id_amount").val(e);
    var i = $(this).find(":selected").attr("data-id");
    $(".gift-card-description-wrapper form").attr("action", "/cart/add/gift/" + i);
}),
    $("document").ready(function () {
        var t = $(".gift-card-amount select").find(":selected").attr("data-id");
        $(".gift-card-description-wrapper form").attr("action", "/cart/add/gift/" + t);
    }),
    $("document").ready(function () {
        var t = $("#products-wrapper .product-element:nth-child(1)").outerWidth(!0),
            e = $("#products-wrapper .product-element:nth-child(2)").outerWidth(!0),
            i = $("#products-wrapper .product-element:nth-child(3)").outerWidth(!0),
            a = $(window).width(),
            d = 0;
        (d = a > 1024 ? t + e + i : a > 834 ? t + e : t), $(".pagination").width(d);
    }),
    $("#detail-page-filter-button").click(function (t) {
        $(this).next().toggleClass("opened"), $(this).toggleClass("closed");
    }),
    $("#mobile-filter-close").click(function (t) {
        $(this).parent().toggleClass("opened"), $("#detail-page-filter-button").toggleClass("closed");
    });
