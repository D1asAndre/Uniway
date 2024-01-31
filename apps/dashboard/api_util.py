import requests

API_BASE_URL = 'http://localhost:8025/'

def obter_registos():
    response = requests.get(f'{API_BASE_URL}registo/')
    return response.json()


def obter_detalhes_registo(id):
    response = requests.get(f'{API_BASE_URL}registo/{id}/')
    return response.json()