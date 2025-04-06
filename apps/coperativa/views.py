from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .models import Cooperativa
from .serializers import CooperativaSerializer


@csrf_exempt
@require_http_methods(["POST"])
def criar_cooperativa(request):
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse(
                {"error": "O corpo da requisição precisa estar em formato JSON válido."},
                status=400
            )

        serializer = CooperativaSerializer(data=data)
        if serializer.is_valid():
            cooperativa = serializer.save()
            return JsonResponse(
                {
                    "message": "Cooperativa criada com sucesso!",
                    "cooperativa": serializer.data
                },
                status=201
            )
        return JsonResponse(
            {"errors": serializer.errors},
            status=400
        )

    except Exception as e:
        return JsonResponse(
            {"error": f"Ocorreu um erro ao processar a requisição: {str(e)}"},
            status=500
        )
