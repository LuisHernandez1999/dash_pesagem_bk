from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import now
from django.db.models import Max, Sum, Count
from apps.pesagem.models import Pesagem
from apps.colaborador.models import Colaborador
from apps.veiculo.models import Veiculo
from apps.coperativa.models import Cooperativa


@csrf_exempt
def criar_pesagem(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            required_fields = [
                'data', 'prefixo_id', 'motorista_id', 'cooperativa_id',
                'hora_chegada', 'hora_saida', 'numero_doc', 'volume_carga'
            ]
            for field in required_fields:
                if field not in data:
                    return JsonResponse({"error": f"EXISTE CAMPO FALATANDO: {field}"}, status=400)

            try:
                veiculo = Veiculo.objects.get(id=data['prefixo_id'])
                motorista = Colaborador.objects.get(id=data['motorista_id'])
                cooperativa = Cooperativa.objects.get(id=data['cooperativa_id'])
                colaboradores = Colaborador.objects.filter(id__in=data.get('colaborador_id', []))
            except ObjectDoesNotExist:
                return JsonResponse({"error": "VEICULO, OU MOTORISTA E CORPORATIVA NÃO ACHADA"}, status=404)

            pesagem = Pesagem(
                data=data.get('data', now().date()),
                prefixo_id=veiculo,
                cooperativa_id=cooperativa,
                responsavel_coop=data.get('responsavel_coop', None),
                motorista_id=motorista,
                hora_chegada=data['hora_chegada'],
                hora_saida=data['hora_saida'],
                numero_doc=data['numero_doc'],
                volume_carga=data['volume_carga'],
            )

            pesagem.peso_calculado = pesagem.calcular_peso()
            pesagem.save()
            pesagem.colaborador_id.set(colaboradores)

            return JsonResponse({
                "id": pesagem.id,
                "data": pesagem.data.strftime('%Y-%m-%d'),
                "prefixo_id": pesagem.prefixo_id.id,
                "tipo_veiculo": pesagem.prefixo_id.tipo,
                "colaborador_id": list(pesagem.colaborador_id.values_list('id', flat=True)),
                "cooperativa_id": pesagem.cooperativa_id.id,
                "responsavel_coop": pesagem.responsavel_coop,
                "motorista_id": pesagem.motorista_id.id,
                "hora_chegada": pesagem.hora_chegada.strftime('%H:%M:%S'),
                "hora_saida": pesagem.hora_saida.strftime('%H:%M:%S'),
                "numero_doc": pesagem.numero_doc,
                "volume_carga": pesagem.volume_carga,
                "peso_calculado": float(pesagem.peso_calculado),
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "O JSON TA ERRADO "}, status=400)

    return JsonResponse({"error": "DEU RUIM"}, status=405)


@csrf_exempt
def exibir_pesagem_por_mes(request):
    if request.method == 'GET':
        try:
            maiores_pesagens_por_mes = (
                Pesagem.objects
                .values("data__year", "data__month")
                .annotate(maior_peso=Max("peso_calculado"))
                .order_by("-data__year", "-data__month")
            )

            resultado = []
            for item in maiores_pesagens_por_mes:
                ano = item["data__year"]
                mes = item["data__month"]
                maior_peso = item["maior_peso"]

                maior_pesagem = Pesagem.objects.filter(
                    data__year=ano, data__month=mes, peso_calculado=maior_peso
                ).first()

                if maior_pesagem:
                    resultado.append({
                        "ano": ano,
                        "mes": mes,
                        "id": maior_pesagem.id,
                        "data": maior_pesagem.data.strftime('%Y-%m-%d'),
                        "prefixo_id": maior_pesagem.prefixo_id.id,
                        "tipo_veiculo": maior_pesagem.prefixo_id.tipo,
                        "motorista_id": maior_pesagem.motorista_id.id,
                        "cooperativa_id": maior_pesagem.cooperativa_id.id,
                        "numero_doc": maior_pesagem.numero_doc,
                        "volume_carga": maior_pesagem.volume_carga,
                        "peso_calculado": float(maior_pesagem.peso_calculado),
                    })

            return JsonResponse({"maiores_pesagens_por_mes": resultado}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "DEU RUIM"}, status=405)


@csrf_exempt
def meta_batida(request):
    if request.method == 'GET':
        try:
            meta = 2601.0  
            batida = Pesagem.objects.aggregate(total_peso=Sum('peso_calculado'))['total_peso'] or 0
            porcentagem = (batida / meta) * 100 if meta > 0 else 0

            return JsonResponse({
                "meta_toneladas": meta,
                "peso_total_batido": round(batida, 2),
                "porcentagem_atingida": round(porcentagem, 2)
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "DEU RUIM"}, status=405)


@csrf_exempt
def ranking_motoristas_com_maiores_pesagens(request):
    if request.method == 'GET':
        try:
            motoristas_ativos = (
                Colaborador.objects
                .filter(funcao='Motorista', status='ATIVO')
            )

            ranking = (
                Pesagem.objects
                .filter(motorista_id__in=motoristas_ativos)
                .values('motorista_id', 'motorista_id__nome')
                .annotate(
                    peso_total=Sum('peso_calculado'),
                    quantidade_pesagens=Count('id')
                )
                .order_by('-peso_total')
            )

            resultado = [
                {
                    "motorista": item['motorista_id__nome'],
                    "peso_total": round(item['peso_total'], 2) if item['peso_total'] else 0.0,
                    "quantidade_pesagens": item['quantidade_pesagens']
                }
                for item in ranking
            ]

            return JsonResponse({"ranking_motoristas": resultado}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "DEU RUIM"}, status=405)


@csrf_exempt
def ranking_cooperativas_com_maiores_pesagens(request):
    if request.method == 'GET':
        try:
            ranking = (
                Pesagem.objects
                .values('cooperativa_id', 'cooperativa_id__nome')
                .annotate(
                    peso_total=Sum('peso_calculado'),
                    quantidade_pesagens=Count('id')
                )
                .order_by('-peso_total')
            )

            resultado = [
                {
                    "cooperativa": item['cooperativa_id__nome'],
                    "peso_total": round(item['peso_total'], 2) if item['peso_total'] else 0.0,
                    "quantidade_pesagens": item['quantidade_pesagens']
                }
                for item in ranking
            ]

            return JsonResponse({"ranking_cooperativas": resultado}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "DEU RUIM"}, status=405)


@csrf_exempt
def media_peso_por_cooperativa(request):
    if request.method == 'GET':
        try:
            media = (
                Pesagem.objects
                .values('cooperativa_id__nome')
                .annotate(
                    media_peso=Sum('peso_calculado') / Count('id'),
                    total_pesagens=Count('id')
                )
                .order_by('-media_peso')
            )

            resultado = [
                {
                    "cooperativa": item['cooperativa_id__nome'],
                    "media_peso": round(item['media_peso'], 2),
                    "total_pesagens": item['total_pesagens']
                }
                for item in media
            ]

            return JsonResponse({"media_por_cooperativa": resultado}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "DEU RUIM"}, status=405)


@csrf_exempt
def eficiencia_por_motorista(request):
    if request.method == 'GET':
        try:
            eficiencia = (
                Pesagem.objects
                .values('motorista_id__nome')
                .annotate(
                    peso_total=Sum('peso_calculado'),
                    quantidade=Count('id'),
                    media_por_viagem=Sum('peso_calculado') / Count('id')
                )
                .order_by('-media_por_viagem')
            )

            resultado = [
                {
                    "motorista": item['motorista_id__nome'],
                    "media_por_viagem": round(item['media_por_viagem'], 2),
                    "viagens": item['quantidade'],
                    "peso_total": round(item['peso_total'], 2)
                }
                for item in eficiencia
            ]
            return JsonResponse({"eficiencia_motoristas": resultado}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "DEU RUIM"}, status=405)

@csrf_exempt
def tipos_pesagem_mais_frequentes(request):
    if request.method == 'GET':
        try:
            tipos_pesagem = (
                Pesagem.objects
                .values('tipo_pesagem')
                .annotate(quantidade=Count('id'))
                .order_by('-quantidade')
            )

            tipo_mais_usado = tipos_pesagem[0] if tipos_pesagem else None

            return JsonResponse({
                "tipos_pesagem": list(tipos_pesagem),
                "tipo_mais_utilizado": tipo_mais_usado
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método não permitido"}, status=405)