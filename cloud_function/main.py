import functions_framework
import requests
from google.cloud import bigquery

client = bigquery.Client()
tabela_destino = 'projetogpc.LANDING_API.endereco_ceps'

@functions_framework.http
def acessar_cep(request):
    sql = "SELECT cep FROM `projetogpc.LANDING_API.ceps`"
    query = client.query(sql)

    for row in query:
        cep = row["cep"]
        url = f'https://viacep.com.br/ws/{cep}/json/'
        response = requests.get(url)
        dados = response.json()

        print(f"Inserindo dados do CEP: {cep}")
        inserir_dados(dados)

    return "Processado"

def inserir_dados(dados):
    errors = client.insert_rows_json(tabela_destino, [dados])
    if errors:
        print("Erro ao inserir dados:", errors)
    else:
        print("Dados inseridos com sucesso")