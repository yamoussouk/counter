import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.template.loader import get_template

log = logging.getLogger(__name__)


class MessageSender:
    def __init__(self, subject, to, sender, message=''):
        self.subject = subject
        self.message = message
        self.to = to
        self.sender = sender

    def send_mail(self):
        sent = send_mail(self.subject, self.message, self.sender, [self.to])
        log.info(
            f"Mail sent to: {self.to}, with the subject of \"{self.subject}\" a message "
            f"of \"{self.message}\", status: \"{sent}\"")
        return sent

    def send_order_confirmation_email(self, data):
        data['STATIC_URL'] = settings.BASE_URL
        plaintext = get_template('email/order_confirmation.txt')
        htmly = get_template('email/order_confirmation_copy.html')
        text_content = plaintext.render(data)
        html_content = htmly.render(data)
        msg = EmailMultiAlternatives(self.subject, text_content, self.sender, [self.to])
        msg.attach_alternative(html_content, "text/html")
        sent = msg.send()
        return sent, text_content

    def send_shipping_confirmation_email(self, data):
        data['STATIC_URL'] = settings.BASE_URL
        plaintext = get_template('email/shipping_confirmation.txt')
        htmly = get_template('email/shipping_confirmation.html')
        text_content = plaintext.render(data)
        html_content = htmly.render(data)
        msg = EmailMultiAlternatives(self.subject, text_content, self.sender, [self.to])
        msg.attach_alternative(html_content, "text/html")
        sent = msg.send()
        return sent, text_content
