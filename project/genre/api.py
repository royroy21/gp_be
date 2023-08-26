from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from project.genre import models, serializers


@require_http_methods(["GET"])
def suggest_genre(request):
    """
    Suggest Genre.

    The URL is made to match the URL used by django_elasticsearch_dsl's
    suggester so this view can be easily converted to use suggester in
    the future.

    An example URL query could be:
    search/genre/suggest/?genre_suggest__completion=ind
    """
    # TODO - convert to Elastic search suggester
    suggest = request.GET.get("genre_suggest__completion")
    query = Q(Q(genre__startswith=suggest) | Q(genre__icontains=suggest))
    result = models.Genre.objects.filter(query).order_by("rank")[
        : settings.PAGE_SIZE
    ]
    return JsonResponse(
        serializers.GenreSerializer(result, many=True).data,
        safe=False,
    )
