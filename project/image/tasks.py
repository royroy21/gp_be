import logging

from celery import shared_task
from django.apps import apps
from django.conf import settings

from project.core.image import exceptions, thumbnail

logger = logging.getLogger(__name__)

retry = {
    "max_retries": 5,
    "countdown": 5,  # retry after 5 seconds.
}


@shared_task(bind=True, queue="thumbnails")
def create_thumbnail(self, app_name, model_name, instance_id):
    if not settings.CREATE_THUMBNAILS_ENABLED:
        logger.debug(
            "Failed to create thumbnail for %s.%s id:%s. Setting not enabled.",
            app_name,
            model_name,
            instance_id,
        )
        return
    try:
        # Starting try/except here, so we always try
        # to get the latest version of the instance.
        Model = apps.get_model(app_name, model_name)  # noqa
        instance = Model.objects.filter(id=instance_id).first()  # noqa
        if not instance:
            logger.error(
                "%s.%s id:%s not found.",
                app_name,
                model_name,
                instance_id,
            )
            return
        logger.debug(
            "task received to create thumbnail for %s.%s id:%s",
            app_name,
            model_name,
            instance_id,
        )
        thumbnail.create_thumbnail(instance)
    except exceptions.ImageHasNotSavedYetException as exc:
        # Probably still waiting for the image
        # to save to the database. Try again.
        raise self.retry(exc=exc, **retry)
