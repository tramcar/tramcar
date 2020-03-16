import bleach
from bleach_whitelist import markdown_tags, markdown_attrs
from django.core.mail import send_mail
from django.conf import settings
import markdown


def convert_markdown(text):
    return bleach.clean(markdown.markdown(text), markdown_tags, markdown_attrs)


def send_mail_with_helper(subject, message, from_email, recipient_list):
    if not settings.DEBUG:
        send_mail(
            subject,
            message,
            from_email,
            recipient_list,
            fail_silently=True,
        )
