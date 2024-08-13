from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from project.instrument import models, serializers


@require_http_methods(["GET"])
def suggest_instrument(request):
    suggest = request.GET.get("instrument_suggest__completion")
    query = Q(
        Q(instrument__startswith=suggest) | Q(instrument__icontains=suggest)
    )
    result = models.Instrument.objects.filter(query).order_by("rank")[
        : settings.PAGE_SIZE
    ]
    return JsonResponse(
        serializers.InstrumentSerializer(result, many=True).data,
        safe=False,
    )
