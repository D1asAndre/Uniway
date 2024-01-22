# djangoProject/run_huey.py
import os
from django import setup
from django.conf import settings
from huey import RedisHuey

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
setup()

# Import Huey após a inicialização do Django
from djangoProject.huey_config import huey

def run_huey():
    print("iniciando")
    huey.create_consumer().run()

if __name__ == '__main__':
    run_huey()
