$("#contact-form").one("submit",function(a){a.preventDefault(),$("#id_email").val($("#contact-email").val()),$("#id_subject").val($("#contact-subject").val()),$("#id_message").val($("#contact-message").val()),$("#id_name").val($("#contact-name").val()),$(this).submit()});