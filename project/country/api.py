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

    An example URL query could be:
    search/country/suggest/?country_suggest__completion=u
    """
    # TODO - convert to Elastic search suggester
    suggest = request.GET.get("country_suggest__completion")
    query = Q(
        Q(country__iexact=suggest)
        | Q(code__iexact=suggest)
        | Q(country__istartswith=suggest)
        | Q(country__icontains=suggest)
        | Q(code__icontains=suggest)
        | Q(code__icontains=suggest)
    )
    result = models.CountryCode.objects.filter(query).order_by("rank")[:5]
    return JsonResponse(
        serializers.CountrySerializer(result, many=True).data,
        safe=False,
    )


@require_http_methods(["GET"])
def get_country(request):
    """
    Get country via ISO country code.

    An example URL query could be:
    api/country/?code=GB
    """
    code = request.GET.get("code", "")
    result = models.CountryCode.objects.filter(code__iexact=code).first()
    response = serializers.CountrySerializer(result).data if result else {}
    return JsonResponse(response, safe=False)
