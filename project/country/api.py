from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from project.country import models, serializers


@require_http_methods(["GET"])
def suggest_country(request):
    """
    Suggest Country.

    The URL is made to match the URL used by django_elasticsearch_dsl's
    suggester so this view can be easily converted to use suggester in
    the future.

    As example URL query could be:
    http://localhost:8000/search/country/suggest/?country_suggest__completion=u
    """
    # TODO - convert to Elastic search suggester
    suggest = request.GET.get("country_suggest__completion")
    query = Q(Q(country__startswith=suggest) | Q(country__icontains=suggest))
    result = models.CountryCode.objects.filter(query).order_by("rank")[:50]
    return JsonResponse(
        serializers.CountrySerializer(result, many=True).data,
        safe=False,
    )
