custom=false;
$(document).ready(function(){
    console.log($('#id_custom').prop('checked'))
    if ($('#id_custom').prop('checked') == true) {
        $(".field-studs").hide();
        $('.field-key_ring').show()
        $('.field-custom_date').show()
        $('.field-initials').show()
        custom=true;
    } else {
        $(".field-studs").show();
        $('.field-key_ring').hide()
        $('.field-custom_date').hide()
        $('.field-initials').hide()
        custom=false;
    }
    $("#id_custom").click(function(){
        custom=!custom;
        if (custom) {
            $(".field-studs").hide();
            $('.field-key_ring').show()
            $('.field-custom_date').show()
            $('.field-initials').show()
        } else {
            $(".field-studs").show();
            $('.field-key_ring').hide()
            $('.field-custom_date').hide()
            $('.field-initials').hide()
        }
    })
})