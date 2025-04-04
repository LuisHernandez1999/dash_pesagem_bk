from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.db import IntegrityError
import json

from .models import Veiculo


@csrf_protect
@require_http_methods(["POST"])
def criar_veiculo(request):
    try:
        data = json.loads(request.body)
        prefixo = data.get("prefixo")
        tipo = data.get("tipo")
        placa_veiculo = data.get("placa_veiculo")
        em_manutencao = data.get("em_manutencao", "NÃO").upper()
        if not prefixo or not tipo:
            return JsonResponse({"error": "os campos 'prefixo' e 'tipo' sao obrigatorios."}, status=400)
        tipos_validos = [t[0] for t in Veiculo.TIPOS_VEICULO]
        if tipo not in tipos_validos:
            return JsonResponse({"error": f"tipo invalido. Tipos permitidos: {tipos_validos}"}, status=400)
        if em_manutencao not in ['SIM', 'NÃO']:
            return JsonResponse({"error": "o campo 'em_manutencao' deve ser 'SIM' ou 'NÃO'."}, status=400)
        veiculo = Veiculo.objects.create(
            prefixo=prefixo,
            tipo=tipo,
            placa_veiculo=placa_veiculo,
            em_manutencao=em_manutencao
        )

        return JsonResponse({
            "message": "veiculo criado com sucesso",
            "veiculo": {
                "id": veiculo.id,
                "prefixo": veiculo.prefixo,
                "tipo": veiculo.tipo,
                "placa_veiculo": veiculo.placa_veiculo,
                "em_manutencao": veiculo.em_manutencao,
            }
        }, status=201)

    except IntegrityError as e:
        return JsonResponse({"error": "prefixo ou placa ja existente no sistema."}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON invalido."}, status=400)

    except Exception as e:
        return JsonResponse({"error": f"ocorreu um erro inesperado: {str(e)}"}, status=500)
