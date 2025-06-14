# Pipeline de Dados com Python, Google Cloud Functions, BigQuery e Apache Airflow

## Descrição do Projeto

Este projeto implementa um pipeline de dados que realiza a extração, armazenamento e orquestração de dados provenientes de uma API pública gratuita. A solução utiliza Python para extração e manipulação dos dados, Google Cloud Functions para execução serverless do código, BigQuery para armazenamento e análise dos dados, e Apache Airflow para orquestrar o fluxo de trabalho de ponta a ponta.

## API Utilizada

Para extração dos dados foi utilizada a API pública gratuita ViaCEP, que retorna informações de endereços a partir do CEP.

Exemplo de endpoint:

`https://viacep.com.br/ws/05312903/json/`

## Componentes da Solução

### 1. Extração de Dados (Python & Cloud Function)

- Um script Python é desenvolvido para consultar a API pública e coletar os dados.
- O script é implementado como uma Google Cloud Function, garantindo execução sob demanda e escalabilidade.
- Os dados brutos extraídos são enviados para uma tabela no BigQuery para armazenamento.

### 2. Armazenamento de Dados (BigQuery)

- Um dataset chamado `LANDING_API` foi criado no BigQuery.
- A Cloud Function grava os dados coletados na tabela `endereco_ceps` dentro deste dataset.
- Esse armazenamento possibilita análises futuras e integrações com outras ferramentas.

### 3. Orquestração (Apache Airflow)

- Uma DAG (Directed Acyclic Graph) foi criada para orquestrar o pipeline.
- A DAG realiza:
  - Acionamento da Cloud Function para extração dos dados.
  - Verificação do carregamento dos dados no BigQuery, garantindo que o processo de ingestão ocorreu com sucesso.
  - Agendamento periódico para execução automatizada do pipeline.


## Como Executar

1. **Deploy da Cloud Function:**
   - Configure seu projeto Google Cloud.
   - Faça deploy do script Python da Cloud Function, garantindo permissão para gravar no BigQuery.

2. **Configuração do BigQuery:**
   - Crie o dataset `LANDING_API`.
   - Crie a tabela `endereco_ceps` ou configure para criação automática conforme o script.

3. **Configuração do Airflow:**
   - Configure a conexão HTTP `google_function_api` para acesso à Cloud Function.
   - Importe a DAG `pipeline.py` para o diretório de DAGs do Airflow.
   - Ajuste o agendamento e execute manualmente ou aguarde execução programada.

## Tecnologias Utilizadas

- Python 3.12.9
- Google Cloud Functions
- Google BigQuery
- Apache Airflow
- Docker (para ambiente Airflow, opcional)
- GitHub (controle de versão)


## Estrutura do Repositório

```
├── cloud_function/
│   └── main.py
├── dags/
│   └── pipeline.py        
├── keys/                  
├── config/                
├── logs/                  
├── plugins/               
├── requirements.txt       
├── docker-compose.yaml    
├── README.md
├── .env                   
└── .gitignore

```

## Configuração das Variáveis de Ambiente

Configure as variáveis no arquivo `.env`:

```env
AIRFLOW_UID=50000
GOOGLE_APPLICATION_CREDENTIALS=/keys/service_account.json
_AIRFLOW_WWW_USER_USERNAME=airflow
_AIRFLOW_WWW_USER_PASSWORD=airflow
```

## Configuração das Conexões no Airflow

Configure a conexão HTTP `google_function_api` com:

- **Tipo:** HTTP  
- **Host:** `https://REGIAO-PROJETO.cloudfunctions.net`  
- **Autenticação:** conforme necessidade (token, sem autenticação, etc)  


## Execução Local

Para rodar o Airflow localmente:

```bash
docker-compose up -d

