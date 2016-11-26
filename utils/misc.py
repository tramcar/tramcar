from django.core.mail import send_mail
from django.conf import settings


def send_mail_with_helper(subject, message, from_email, recipient_list):
    if not settings.DEBUG:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=True,
        )
