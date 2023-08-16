import logging

from celery import shared_task
from django.conf import settings

from project.core.image import exceptions, thumbnail
from project.gig import models

logger = logging.getLogger(__name__)

retry = {
    "max_retries": 5,
    "countdown": 5,  # retry after 5 seconds.
}


@shared_task(bind=True, queue="thumbnails")
def create_gig_thumbnail(self, gig_id):
    if not settings.CREATE_THUMBNAILS_ENABLED:
        logger.debug(
            "Cannot create thumbnail for gig:%s. Setting not enabled.",
            gig_id,
        )
        return
    try:
        # Starting try/except here, so we always try
        # to get the latest version of the instance.
        gig = models.Gig.objects.filter(id=gig_id).first()
        if not gig:
            logger.error("gig with id:%s not found.", gig_id)
            return
        logger.debug(
            "task received to create thumbnail for gig:%s",
            gig_id,
        )
        thumbnail.create_thumbnail(gig)
    except exceptions.ImageHasNotSavedYetException as exc:
        # Probably still waiting for the image
        # to save to the database. Try again.
        raise self.retry(exc=exc, **retry)
