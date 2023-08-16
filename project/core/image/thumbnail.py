import logging
import re
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image

from project.core.image import exceptions

logger = logging.getLogger(__name__)

THUMBNAIL_SIZE = (150, 150)
THUMBNAIL_NAME = "thumbnail"


def create_thumbnail(instance):
    if not hasattr(instance, "image") or not hasattr(instance, "thumbnail"):
        logger.error(
            "Instance %s is missing image and/or thumbnail field.",
            instance,
        )
        return

    if not instance.image:
        logger.error(
            "Instance %s has no file saved at image field.",
            instance,
        )
        raise exceptions.ImageHasNotSavedYetException

    resized_image_io = resize_image(instance.image)
    resized_image_name = get_resized_image_name(instance.image.name)
    logger.debug(
        "Creating thumbnail %s for instance %s.",
        instance,
        resized_image_name,
    )
    instance.thumbnail.save(
        resized_image_name,
        ContentFile(resized_image_io.getvalue()),
    )
    logger.debug(
        "Saving thumbnail %s to instance %s.",
        instance,
        resized_image_name,
    )
    instance.save()


def resize_image(original_image):
    image = Image.open(original_image)
    image.thumbnail(THUMBNAIL_SIZE)
    image_io = BytesIO()
    image.save(
        image_io,
        format=image.format,
        compress_level=5,
        optimize=True,
        quality=100,
        subsampling=0,
    )
    return image_io


def get_resized_image_name(name):
    name_removed_directory = "".join(name.split("/")[1:])
    name_split = re.split("(\.)", name_removed_directory)  # noqa
    name_split.insert(-2, f"-{THUMBNAIL_NAME}")
    return "".join(name_split)
