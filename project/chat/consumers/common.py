import logging

logger = logging.getLogger(__name__)


def format_user(user):
    return {"id": user.id, "username": user.username}


def log_error(scope, message):
    if scope["user"].is_authenticated:
        user = format_user(scope["user"])
    else:
        user = "not authenticated"
    url_data = f"path:{scope['path']}, arguments:{scope['url_route']}"
    return logger.error("%s for user:%s, %s", message, user, url_data)
