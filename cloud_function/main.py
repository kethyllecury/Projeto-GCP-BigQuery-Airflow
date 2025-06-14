
import functions_framework
import requests
from google.cloud import bigquery
import json

tabela_id = 'projetogpc.LANDING_API.endereco_ceps'
client = bigquery.Client()
tabela = client.get_table(tabela_id)

@functions_framework.http
def acessar_cep(request):
    cep = request.args.get('cep')
    if not cep:
        return 'informe o cep ex: 51010-050 ou 51010050'

    dados = tratar_cep(cep)
    if isinstance(dados, dict):
        inserir_dados(dados)
        return dados
    else:
        return 'cep inválido'

def tratar_cep(cep):
    cep = cep.strip()
    cep_limpo = cep.replace('-', '')

    if len(cep_limpo) == 8 and cep_limpo.isdigit():
        url = f'https://viacep.com.br/ws/{cep_limpo}/json/'
        resposta = requests.get(url)
        dados = resposta.json()
        return dados
    else:
        return 'cep inválido'

def inserir_dados(dados):
    try:
        client.insert_rows_json(tabela, [dados])
        print("dados inseridos")
    except Exception as e:
        print("erro ao inserir:", e)

