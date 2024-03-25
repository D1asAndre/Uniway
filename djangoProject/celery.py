from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Definir a variável de ambiente padrão do Django para o arquivo de configuração do setting.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.py')

app = Celery('djangoProject')

# Usar a string de configuração do celery no arquivo settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')

# Cerrega as tarefas de todas as aplicações
app.autodiscover_tasks()