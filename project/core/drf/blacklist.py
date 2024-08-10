import logging

from rest_framework_simplejwt.token_blacklist import models

logger = logging.getLogger(__name__)


def blacklist_user_tokens(user):
    tokens = models.OutstandingToken.objects.filter(user=user)
    for token in tokens:
        _, created = models.BlacklistedToken.objects.get_or_create(token=token)
        if created:
            logger.info(f"Token {token} blacklisted.")
        else:
            logger.info(f"Token {token} was already blacklisted.")
