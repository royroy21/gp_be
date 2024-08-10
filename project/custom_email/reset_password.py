from django.conf import settings

from project.custom_email.base import Email


def send_reset_password_email(to_address, token):
    # TODO - change to https!!!
    # message = f'Click <a href="https://{settings.FRONTEND_DOMAIN}/reset-password/{token}">here</a> to reset your password.'  # noqa
    message = f'Click <a href="http://{settings.FRONTEND_DOMAIN}/reset-password/{token}">here</a> to reset your password.'  # noqa
    Email.send_single_email(
        message=Email.generate_html_template(message),
        to_address=to_address,
    )
