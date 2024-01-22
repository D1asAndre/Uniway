# djangoProject/huey_config.py

import json
from huey import crontab
from huey.contrib.djhuey import db_periodic_task
from huey import RedisHuey
import logging
from django.core.mail import send_mail
from datetime import datetime, timedelta
from django.http import JsonResponse

huey = RedisHuey('my-huey-queue')
logger = logging.getLogger(__name__)

@huey.task()
def enviar_email_boleia_agendada (user_email, boleia_instance_id):
    from apps.addboleia.models import Boleia, HistoricoBoleia, PedidoBoleia #não retirar
    
    boleia_instance = Boleia.objects.get(id=boleia_instance_id)


    try:

        logger.info('Iniciando envio de e-mail assíncrono...')
        
        # Crie uma mensagem de e-mail
        subject = 'Assunto do E-mail'
        body = 'Estamos a enviar este email  para informar-lhe que sua boleia foi dado como concluido'
        from_email = 'uniway@outlook.pt'  # Altere aqui para o endereço desejado
        to_email = [user_email]  # Alterado para o email do usuário

        # Envie o e-mail usando a função send_mail
        send_mail(subject, body, from_email, to_email)

        # Adicione logs indicando o início do processo de envio de e-mail
        logger.info(f'Enviando e-mail de {from_email} para {to_email} com o assunto: {subject}')
        
        dados_pedidos = []
        for pedido in PedidoBoleia.objects.filter(boleia=boleia_instance):
            dados_pedidos.append({
                'passageiro_username': pedido.passageiro.username,
                'origem': pedido.boleia.origem,
                'destino': pedido.boleia.destino,
                'data_pedido': pedido.data_pedido.strftime('%Y-%m-%d %H:%M:%S'),
                'motorista_username': boleia_instance.user.username,
                'data_boleia': boleia_instance.data.strftime('%Y-%m-%d'),
                'hora_boleia': boleia_instance.hora.strftime('%H:%M:%S'),
                'aceito': pedido.aceito,  
            })

        # Tenta abrir o arquivo JSON existente
        try:
            with open('apps/addboleia/pedidos_boleia.json', 'r') as arquivo_json:
                dados_json = json.load(arquivo_json)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            # Se o arquivo não existir ou não for um JSON válido, cria um dicionário vazio
            dados_json = {'pedidos': []}

        # Adiciona os novos dados aos existentes
        dados_json['pedidos'].extend(dados_pedidos)

        # Escrever os dados de volta no arquivo JSON
        from django.core.serializers.json import DjangoJSONEncoder

        with open('apps/addboleia/pedidos_boleia.json', 'w') as arquivo_json:
            json.dump(dados_json, arquivo_json, cls=DjangoJSONEncoder)

            
        HistoricoBoleia.objects.create(
            user=boleia_instance.user,
            origem=boleia_instance.origem,
            destino=boleia_instance.destino,
            vagas_disponiveis=boleia_instance.vagas_disponiveis,
            vagas_ocupadas=boleia_instance.vagas_ocupadas,
            data=boleia_instance.data,
            hora=boleia_instance.hora,
            cancelada=False  # Você pode ajustar isso conforme necessário
        )

        # Remova a boleia da tabela Boleia
        boleia_instance.delete()
        
        


        # Adicione logs indicando o sucesso no agendamento de e-mail
        logger.info('E-mail agendado com sucesso!')

    except Exception as e:
        logger.error(f'Erro ao enviar e-mail assíncrono: {e}')