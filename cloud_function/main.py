import functions_framework
import requests
from google.cloud import bigquery

client = bigquery.Client()
tabela_destino = 'projetogpc.LANDING_API.endereco_ceps'

@functions_framework.http
def acessar_cep(request):
    sql = "select cep from `projetogpc.LANDING_API.ceps`"
    query = client.query(sql)

    for row in query:
        cep = row["cep"]
        url = f'https://viacep.com.br/ws/{cep}/json/'
        response = requests.get(url)
        dados = response.json()

        print(f"cep inserido: {cep}")
        inserir_dados(dados)

    return "dados processados no bigquery"

def inserir_dados(dados):
    try:
        client.insert_rows_json(tabela_destino, [dados])
        print("dados inseridos")
    except Exception as e:
        print("erro ao inserir dados:", e)
