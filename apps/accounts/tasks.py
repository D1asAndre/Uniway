from datetime import datetime, timedelta

from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone

from apps.accounts.models import CustomUser

@shared_task
def check_and_notify_inactive_users():
    """
    Usuários Inativos há Quase Um Ano: Seleciona usuários que estão inativos há quase um ano (mas não ultrapassaram esse período)
    e envia um e-mail de aviso sobre a iminente eliminação da conta.
    Usuários que Não Ativaram a Conta: Seleciona usuários que criaram
    uma conta mas não a ativaram dentro de aproximadamente um mês e
    envia um e-mail instruindo a ativação para evitar a eliminação.
    :return:
    """

    today = datetime.now()
    year_ago = today - timedelta(days=364)
    month_ago = today - timedelta(days=29)

    # Verificar e notifica user com contas inativas por quase um ano
    nearly_year_inactive_users = CustomUser.objects.filter(
        is_active=True,
        inactivity_date__lte=year_ago + timedelta(days=30),
        inactivity_date__gt=year_ago
    )

    for user in nearly_year_inactive_users:
        send_mail(
            'Sua conta será em breve eliminada',
            f'Exmo {user.username} sua conta encontra-se inativa há quase um ano e será em breve eliminada da plataforma',
            'uniway@outlook.pt',
            [user.email],
            fail_silently=False,
        )

    # Verificar e notificar user que não ativaram a conta na plataforma a quase um mês
    nearly_month_inactive_users = CustomUser.objects.filter(
        is_active=False,
        date_joined__lte=month_ago + timedelta(days=1),
        date_joined__gt=month_ago
    )

    for user in nearly_month_inactive_users:
        send_mail(
            'Sua conta será em breve eliminada',
            f'Exmo {user.username} sua conta não está ativa na plataforma por favor ative a sua conta "link para ativação", senão a sua conta será eliminada da plataforma',
            'uniway@outlook.pt',
            fail_silently=False,
        )

@shared_task
def delete_inactive_accounts():
    # Define a data um ano atrás
    one_year_ago = timezone.now() - timedelta(days=365)

    # Elimina contas inativas há mais de um ano
    CustomUser.objects.filter(is_active=True, inactivity_date__lte=one_year_ago).delete()

    # Defini a data um mês atrás
    one_month_ago = timezone.now() - timedelta(days=30)

    # Elimina contas não ativadas há mais de 1 mês
    CustomUser.objects.filter(is_active=False, date_joined__lte=one_month_ago).delete()