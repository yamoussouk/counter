$('#contact-form').one('submit', function(e) {
    e.preventDefault();

    $('#id_email').val($('#contact-email').val())
    $('#id_subject').val($('#contact-subject').val())
    $('#id_message').val($('#contact-message').val())

    $(this).submit();
});