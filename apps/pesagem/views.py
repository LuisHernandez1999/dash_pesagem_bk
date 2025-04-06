from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import localtime
from django.utils.timezone import now
from datetime import timedelta
from django.db.models import Max, Sum,Count
from apps.pesagem.models import Pesagem
from apps.colaborador.models import Colaborador
from apps.veiculo.models import Veiculo
from apps.coperativa.models import Cooperativa
from collections import defaultdict


@csrf_exempt
def criar_pesagem(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            required_fields = [
                'data', 'prefixo_id', 'motorista_id', 'cooperativa_id',
                'hora_chegada', 'hora_saida', 'numero_doc', 'volume_carga', 'tipo_pesagem'
            ]
            for field in required_fields:
                if field not in data:
                    return JsonResponse({"error": f"Campo obrigatório faltando: {field}"}, status=400)

            try:
                veiculo = Veiculo.objects.get(id=data['prefixo_id'])
                motorista = Colaborador.objects.get(id=data['motorista_id'])
                cooperativa = Cooperativa.objects.get(id=data['cooperativa_id'])
                colaboradores = Colaborador.objects.filter(id__in=data.get('colaborador_id', []))
            except ObjectDoesNotExist:
                return JsonResponse({"error": "Veículo, motorista ou cooperativa não encontrados."}, status=404)

            pesagem = Pesagem(
                data=data.get('data', now().date()),
                prefixo_id=veiculo,
                cooperativa_id=cooperativa,
                responsavel_coop=data.get('responsavel_coop'),
                motorista_id=motorista,
                hora_chegada=data['hora_chegada'],
                hora_saida=data['hora_saida'],
                numero_doc=data['numero_doc'],
                volume_carga=data['volume_carga'],
                tipo_pesagem=data['tipo_pesagem']
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
                "tipo_pesagem": pesagem.tipo_pesagem,
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido."}, status=400)
        except Exception as e:
            return JsonResponse({"error": f"Erro interno: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método não permitido."}, status=405)


@csrf_exempt
def quantidade_de_pesagens(request):
    if request.method == 'GET':
        total_pesagens = Pesagem.objects.count()
        return JsonResponse({"quantidade_de_pesagens": total_pesagens}, status=200)
    return JsonResponse({"error": "Método não permitido."}, status=405)


@csrf_exempt
def quantidade_de_toneladas_pesadas(request):
    if request.method == 'GET':
        resultado = Pesagem.objects.aggregate(total_peso=Sum('peso_calculado'))
        total_peso = resultado['total_peso'] or 0
        return JsonResponse({"total_toneladas_pesadas": float(total_peso)}, status=200)
    return JsonResponse({"error": "Método não permitido."}, status=405)


@csrf_exempt
def exibir_pesagem_por_mes(request):
    if request.method == 'GET':
        try:
            pesagens = Pesagem.objects.all()
            agrupado = defaultdict(lambda: {'quantidade': 0, 'peso_total': 0.0})

            for p in pesagens:
                data = localtime(p.data)  
                tipo = p.tipo_pesagem
                peso = p.peso_calculado or 0
                if data.day >= 20:
                    ref_ano = data.year
                    ref_mes = data.month
                else:
                    anterior = data.replace(day=1) - timedelta(days=1)
                    ref_ano = anterior.year
                    ref_mes = anterior.month

                chave = (ref_ano, ref_mes, tipo)
                agrupado[chave]['quantidade'] += 1
                agrupado[chave]['peso_total'] += peso

            resultado = []
            for (ano, mes, tipo), valores in sorted(agrupado.items(), reverse=True):
                resultado.append({
                    "ano": ano,
                    "mes_referencia": mes,
                    "tipo_pesagem": tipo,
                    "quantidade_pesagens": valores['quantidade'],
                    "peso_total": round(valores['peso_total'], 2),
                })

            return JsonResponse({"pesagens_por_periodo_personalizado": resultado}, status=200)

        except Exception as e:
            return JsonResponse({"error": f"Erro ao processar: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método não permitido."}, status=405)

@csrf_exempt
def meta_batida(request):
    if request.method == 'GET':
        try:
            meta = 2601.0  
            batida = Pesagem.objects.aggregate(total_peso=Sum('peso_calculado'))['total_peso'] or 0
            porcentagem = (batida / 1000) / (meta / 1000) * 100 if meta > 0 else 0

            return JsonResponse({
                "meta_toneladas": meta,
                "peso_total_batido": round(batida, 2),
                "porcentagem_atingida": round(porcentagem, 2)
            }, status=200)

        except Exception as e:
            return JsonResponse({"error": f"Erro ao calcular meta: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método não permitido."}, status=405)

@csrf_exempt
def def_pesagens_seletiva(request):
    if request.method == 'GET':
        try:
            total_seletiva = Pesagem.objects.filter(tipo_pesagem='SELETIVA').count()
            return JsonResponse({"total_pesagens_seletiva": total_seletiva}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"erro ao contar pesagens seletivas: {str(e)}"}, status=500)

    return JsonResponse({"error": "metodo nao permitido"}, status=405)

@csrf_exempt
def def_pesagens_cata_treco(request):
    if request.method == 'GET':
        try:
            total_cata_treco = Pesagem.objects.filter(tipo_pesagem='CATA TRECO').count()
            return JsonResponse({"total_pesagens_cata_treco": total_cata_treco}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Erro ao contar pesagens cata treco: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método não permitido"}, status=405)

@csrf_exempt
def def_pesagens_ao_longo_ano_por_tipo_pesagem(request):
    if request.method == 'GET':
        try:
            from django.db.models.functions import ExtractMonth, ExtractYear
            dados = (
                Pesagem.objects
                .annotate(ano=ExtractYear('data'), mes=ExtractMonth('data'))
                .values('ano', 'mes', 'tipo_pesagem')
                .annotate(total=Count('id'))
                .order_by('ano', 'mes')
            )
            resultado = {}
            for item in dados:
                ano = item['ano']
                mes = item['mes']
                tipo = item['tipo_pesagem']
                total = item['total']
                chave = f"{ano}-{mes:02d}"
                if chave not in resultado:
                    resultado[chave] = {
                        'total_geral': 0,
                        'SELETIVA': 0,
                        'CATA TRECO': 0,
                        'OUTROS': 0
                    }
                resultado[chave]['total_geral'] += total
                if tipo == 'SELETIVA':
                    resultado[chave]['SELETIVA'] += total
                elif tipo == 'CATA TRECO':
                    resultado[chave]['CATA TRECO'] += total
                else:
                    resultado[chave]['OUTROS'] += total
            return JsonResponse({"pesagens_ao_longo_ano": resultado}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Erro ao calcular pesagens por tipo: {str(e)}"}, status=500)
    return JsonResponse({"error": "Método não permitido"}, status=405)

@csrf_exempt
def top_5_coperativas_por_pesagem(request):
    if request.method == 'GET':
        try:
            total_pesagens = Pesagem.objects.count()
            if total_pesagens == 0:
                return JsonResponse({"message": "Nenhuma pesagem encontrada."}, status=200)
            cooperativas = (
                Pesagem.objects
                .values('cooperativa_id__nome') 
                .annotate(total=Count('id'))
                .order_by('-total')[:5]
            )
            resultado = []
            for item in cooperativas:
                nome = item['cooperativa_id__nome']
                total = item['total']
                porcentagem = round((total / total_pesagens) * 100, 2)
                resultado.append({
                    "cooperativa": nome,
                    "total_pesagens": total,
                    "porcentagem": f"{porcentagem}%",
                })
            return JsonResponse({"top_5_cooperativas": resultado}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Erro ao buscar cooperativas: {str(e)}"}, status=500)
    return JsonResponse({"error": "Método não permitido"}, status=405)

@csrf_exempt
def veiculo_maior_pesagens(request):
    if request.method == 'GET':
        try:
            veiculo = (
                Pesagem.objects
                .values('prefixo_id__prefixo', 'prefixo_id__tipo')
                .annotate(total_pesagens=Count('id'))
                .order_by('-total_pesagens')
                .first()
            )
            if not veiculo:
                return JsonResponse({"message": "Nenhuma pesagem encontrada."}, status=200)
            resultado = {
                "prefixo": veiculo['prefixo_id__prefixo'],
                "tipo_veiculo": veiculo['prefixo_id__tipo'],
                "quantidade_de_pesagens": veiculo['total_pesagens']
            }
            return JsonResponse({"veiculo_com_mais_pesagens": resultado}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Erro ao buscar veículo: {str(e)}"}, status=500)
    return JsonResponse({"error": "Método não permitido"}, status=405)

@csrf_exempt
def eficiencia_motoristas(request):
    if request.method == 'GET':
        try:
            motoristas = (
                Pesagem.objects
                .values('motorista_id__id', 'motorista_id__nome')  
                .annotate(
                    total_volume=Sum('volume_carga'),
                    total_pesagens=Count('id')
                )
            )
            for m in motoristas:
                m['media_volume'] = m['total_volume'] / m['total_pesagens'] if m['total_pesagens'] else 0
            maior_media = max([m['media_volume'] for m in motoristas], default=1)
            resultado = []
            for m in motoristas:
                eficiencia_pct = round((m['media_volume'] / maior_media) * 100, 2) if maior_media else 0

                resultado.append({
                    'motorista_id': m['motorista_id__id'],
                    'nome': m['motorista_id__nome'],
                    'total_volume': m['total_volume'],
                    'total_pesagens': m['total_pesagens'],
                    'eficiencia_percentual': eficiencia_pct,
                })
            resultado.sort(key=lambda x: x['eficiencia_percentual'], reverse=True)
            return JsonResponse({'eficiencia_motoristas': resultado}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Erro ao calcular eficiência: {str(e)}"}, status=500)
    return JsonResponse({"error": "Método não permitido"}, status=405)

@csrf_exempt
def eficiencia_veiculos(request):
    if request.method == 'GET':
        try:
            veiculos = (
                Pesagem.objects
                .values('prefixo_id__id', 'prefixo_id__prefixo')
                .annotate(
                    total_volume=Sum('volume_carga'),
                    total_pesagens=Count('id')
                )
            )
            for v in veiculos:
                v['media_volume'] = v['total_volume'] / v['total_pesagens'] if v['total_pesagens'] else 0
            maior_media = max([v['media_volume'] for v in veiculos], default=1)
            resultado = []
            for v in veiculos:
                eficiencia_pct = round((v['media_volume'] / maior_media) * 100, 2) if maior_media else 0
                resultado.append({
                    'veiculo_id': v['prefixo_id__id'],
                    'prefixo': v['prefixo_id__prefixo'],
                    'total_volume': v['total_volume'],
                    'total_pesagens': v['total_pesagens'],
                    'eficiencia_percentual': eficiencia_pct,
                })
            resultado.sort(key=lambda x: x['eficiencia_percentual'], reverse=True)
            return JsonResponse({'eficiencia_veiculos': resultado}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Erro ao calcular eficiência: {str(e)}"}, status=500)
    return JsonResponse({"error": "Método não permitido"}, status=405)


@csrf_exempt
def eficiencia_cooperativas(request):
    if request.method == 'GET':
        try:
            cooperativas = (
                Pesagem.objects
                .values('cooperativa_id__id', 'cooperativa_id__nome')
                .annotate(
                    total_volume=Sum('volume_carga'),
                    total_pesagens=Count('id')
                )
            )
            for c in cooperativas:
                c['media_volume'] = c['total_volume'] / c['total_pesagens'] if c['total_pesagens'] else 0
            maior_media = max([c['media_volume'] for c in cooperativas], default=1)
            resultado = []
            for c in cooperativas:
                eficiencia_pct = round((c['media_volume'] / maior_media) * 100, 2) if maior_media else 0
                resultado.append({
                    'cooperativa_id': c['cooperativa_id__id'],
                    'nome': c['cooperativa_id__nome'],
                    'total_volume': c['total_volume'],
                    'total_pesagens': c['total_pesagens'],
                    'eficiencia_percentual': eficiencia_pct,
                })
            resultado.sort(key=lambda x: x['eficiencia_percentual'], reverse=True)
            return JsonResponse({'eficiencia_cooperativas': resultado}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Erro ao calcular eficiência: {str(e)}"}, status=500)
    return JsonResponse({"error": "Método não permitido"}, status=405)