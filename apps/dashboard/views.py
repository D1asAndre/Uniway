from ast import Is
from datetime import datetime

import googlemaps
import requests
from django.shortcuts import render
from apps.addboleia.models import Boleia, HistoricoBoleia
from django.db.models import Count, Sum, Case, When, IntegerField
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from .api_util import obter_detalhes_registo, obter_registos


# Create your views here.
@user_passes_test(lambda user: user.is_superuser)
def dashboardView(request):
    """
    Havia feito essa query em SQL:
    SELECT destino, COUNT(destino) AS quantidade
    FROM addboleia_boleia
    GROUP BY destino;
    Mas pra ter mais Segurança utilizei a função ORM do django para pegar os dados da base de dados
    """

    destinos_contados = list(Boleia.objects.values('destino').annotate(quantidade=Count('destino')))

    destinos_historico = list(
        HistoricoBoleia.objects.filter(cancelada=False).values('destino').annotate(quantidade=Count('destino')))

    # destinos_historico_contados = list(HistoricoBoleia.objects.values('destino').annotate(quantidade=Count('destino'),cancelada=Sum('cancelada')))

    destinos_historico_contados = list(
        HistoricoBoleia.objects.values('destino')
        .annotate(
            quantidade=Count('destino'),
            quantidade_cancelada=Sum(
                Case(
                    When(cancelada=True, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            ),
            quantidade_finalizada=Sum(
                Case(
                    When(cancelada=False, then=1),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )
    )

    destinos_vagas = list(HistoricoBoleia.objects.filter(cancelada=False).values('destino').annotate(
        vagas_disponiveis=Sum('vagas_disponiveis'), vagas_ocupadas=Sum('vagas_ocupadas')))

    origens_local = list(Boleia.objects.values('origem', 'destino'))

    # print(destinos_contados)
    print(destinos_historico_contados)
    # print(destinos_vagas)

    # Calcula o total de km e emissoes CO2
    total_km, total_emissoes = calcular_total_distancias_emissoes()

    context = {
        'destinos_contados': destinos_contados,
        'origens_local': origens_local,
        'destinos_historico_contados': destinos_historico_contados,
        'destinos_historico': destinos_historico,
        'total_km': total_km,
        'total_emissoes': total_emissoes
    }
    return render(request, 'indexDash.html', context)


def listarRegistos(request):
    registo = obter_registos()
    return render(request, 'listar.html', {'registo': registo})


def listarRegistosPorId(request, id):
    registo = obter_detalhes_registo(id)
    return render(request, 'listarId.html', {'registo': registo})


def get_distance(origem, destino):
    gmaps = googlemaps.Client(key='<KEY>') # Usar a chave da api
    agora = datetime.now()
    distance_result  = gmaps.distance_matrix(origem, destino, mode="driving", departure_time=agora)

    # Obter distancia em metros
    distance_in_meters = distance_result['row'][0]['elemets'][0]['distance']['value']
    return distance_in_meters / 1000 # Retorna em Km

def calcular_emissoes_co2(distancia_km):
    fator_emissoes_co2 = 0.120  # 120g por km
    emissao_co2 = distancia_km * fator_emissoes_co2
    return emissao_co2

def calcular_total_distancias_emissoes():
    total_km = 0
    total_emissoes = 0

    for boleia in HistoricoBoleia.objects.filter(cancelada=False):
        distancia = get_distance(boleia.origem, boleia.destino)
        total_km += distancia
        total_emissoes += calcular_emissoes_co2(distancia)

    return total_km, total_emissoes