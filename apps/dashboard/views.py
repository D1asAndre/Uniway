from ast import Is

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

    context = {
        'destinos_contados': destinos_contados,
        'origens_local': origens_local,
        'destinos_historico_contados': destinos_historico_contados,
        'destinos_historico': destinos_historico
    }
    return render(request, 'indexDash.html', context)


def listarRegistos(request):
    registo = obter_registos()
    return render(request, 'listar.html', {'registo': registo})


def listarRegistosPorId(request, id):
    registo = obter_detalhes_registo(id)
    return render(request, 'listarId.html', {'registo': registo})
