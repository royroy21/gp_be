import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from django.conf import settings

logger = logging.getLogger(__name__)


class Email:
    host = settings.EMAIL_HOST
    port = settings.EMAIL_PORT
    user = settings.EMAIL_USER
    password = settings.EMAIL_PASSWORD
    from_email = settings.EMAIL_DEFAULT_FROM
    default_subject = settings.EMAIL_DEFAULT_SUBJECT

    @classmethod
    def send_single_email(cls, message, to_address, subject=None):
        if not subject:
            subject = cls.default_subject

        smtp = smtplib.SMTP(cls.host, port=cls.port)
        smtp.starttls()
        try:
            smtp.login(cls.user, cls.password)
            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg.attach(MIMEText(message, "html"))
            smtp.sendmail(cls.from_email, to_address, msg.as_string())
        except Exception as error:
            logger.error("Error sending email to %s: %s", to_address, error)
        finally:
            smtp.quit()
            logger.debug("Email sent to %s", to_address)

    @classmethod
    def generate_html_template(cls, message):
        return f"""
        <html>
            <body>
                <p>{message}</p>
            </body>
        </html>
        """
