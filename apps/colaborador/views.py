import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from .models import Colaborador

@csrf_protect
@require_http_methods(["POST"])
def criar_colaborador(request):
    try:
        data = json.loads(request.body)

        colaborador = Colaborador.objects.create(
            nome=data['nome'],
            matricula=data['matricula'],
            funcao=data['funcao'],
            turno=data['turno'],
            status=data['status'],
            pa=data['pa']
        )

        return JsonResponse({
            "id": colaborador.id,
            "nome": colaborador.nome,
            "matricula": colaborador.matricula,
            "funcao": colaborador.funcao,
            "turno": colaborador.turno,
            "status": colaborador.status,
            "pa": colaborador.pa,
        }, status=201)

    except KeyError as e:
        return JsonResponse({"error": f"Campo obrigatório ausente: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
