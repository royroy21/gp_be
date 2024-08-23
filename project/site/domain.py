from django.conf import settings
from django.contrib.sites.models import Site


def build_absolute_uri(relative_uri):
    """
    Uses Site framework to provide absolute URL
    for when request object is not available.
    """
    if relative_uri.startswith("http"):
        # Relative URL already has full domain
        return relative_uri

    domain = Site.objects.get_current().domain
    return f"{settings.SITE_SCHEME}://{domain}{relative_uri}"
