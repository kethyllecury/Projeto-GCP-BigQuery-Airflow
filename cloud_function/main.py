import functions_framework
import requests

@functions_framework.http
def acessar_cep(request):
    cep = request.args.get('cep')

    if not cep:
        return "Digite o CEP corretamente, por exemplo: 51021-020"

    url = f'https://viacep.com.br/ws/{cep}/json/'
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return f"Falha ao consultar o CEP {cep}"