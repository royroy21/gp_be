import logging

import exponent_server_sdk
from celery import shared_task
from requests.exceptions import ConnectionError, HTTPError

from project.custom_user import models

logger = logging.getLogger(__name__)


retry = {
    "max_retries": 5,
    "countdown": 5,  # retry after 5 seconds.
}


@shared_task(bind=True, queue="push_notifications")
def send_push_notification(self, user_id, title, message, data):
    """
    Sends a push notification to all user's active devices.
    """
    user = models.User.objects.filter(id=user_id).first()
    if not user:
        logger.error("user with id:%s not found.", user_id)
        return

    for token in user.notification_tokens.filter(active=True):
        variables = {
            "to": token.token,
            "title": title,
            "body": message,
            "data": data,
        }
        logger.debug(
            "attempting to send push notification "
            "to user with id:%s using:%s.",
            user.id,
            variables,
        )
        try:
            response = exponent_server_sdk.PushClient().publish(
                exponent_server_sdk.PushMessage(**variables)
            )
        except exponent_server_sdk.PushServerError as exc:
            logger.error(
                "PushServerError for user:%s, using:%s, "
                "errors:%s, response_data:%s.",
                user.id,
                variables,
                exc.errors,
                exc.response_data,
            )
            return
        except (ConnectionError, HTTPError) as exc:
            logger.error(
                "ConnectionError or HTTPError for user:%s, using:%s. "
                "Retrying ...",
                user.id,
                variables,
            )
            raise self.retry(exc=exc, **retry)

        logger.debug(
            "Push notification response received "
            "for user:%s, using:%s, response:%s.",
            user.id,
            variables,
            response.status,
        )
        try:
            response.validate_response()
        except exponent_server_sdk.DeviceNotRegisteredError:
            logger.debug(
                "DeviceNotRegisteredError for user:%s, using:%s. "
                "setting token to not active.",
                user.id,
                variables,
            )
            token.active = False
            token.save()
            return
        except exponent_server_sdk.PushTicketError as exc:
            # Encountered some other per-notification error.
            logger.error(
                "PushTicketError for user:%s, using:%s, push_response:%s. "
                "Retrying ...",
                user.id,
                variables,
                exc.push_response._asdict(),  # noqa
            )
            raise self.retry(exc=exc, **retry)
