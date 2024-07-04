from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from project.genre import models, serializers


@require_http_methods(["GET"])
def suggest_genre(request):
    suggest = request.GET.get("genre_suggest__completion")
    query = Q(Q(genre__startswith=suggest) | Q(genre__icontains=suggest))
    result = models.Genre.objects.filter(query).order_by("rank")[
        : settings.PAGE_SIZE
    ]
    return JsonResponse(
        serializers.GenreSerializer(result, many=True).data,
        safe=False,
    )
