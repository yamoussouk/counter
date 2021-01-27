import base64
import logging
import os

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
        email_logo = os.path.join(settings.STATIC_ROOT, 'images', 'email_logo.png')
        submark_logo = os.path.join(settings.STATIC_ROOT, 'images', 'submark_150.png')
        facebook_logo = os.path.join(settings.STATIC_ROOT, 'images', 'facebook_150.png')
        instagram_logo = os.path.join(settings.STATIC_ROOT, 'images', 'instagram_150.png')
        with open(email_logo, "rb") as image_file:
            encoded_email_logo = base64.b64encode(image_file.read())
        with open(submark_logo, "rb") as image_file:
            encoded_submark_logo = base64.b64encode(image_file.read())
        with open(facebook_logo, "rb") as image_file:
            encoded_facebook_logo = base64.b64encode(image_file.read())
        with open(instagram_logo, "rb") as image_file:
            encoded_instagram_logo = base64.b64encode(image_file.read())
        data['STATIC_URL'] = settings.BASE_URL
        data['EMAIL_LOGO'] = encoded_email_logo
        data['SUBMARK_LOGO'] = encoded_submark_logo
        data['FACEBOOK_LOGO'] = encoded_facebook_logo
        data['INSTAGRAM_LOGO'] = encoded_instagram_logo
        plaintext = get_template('email/order_confirmation.txt')
        htmly = get_template('email/order_confirmation.html')
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
