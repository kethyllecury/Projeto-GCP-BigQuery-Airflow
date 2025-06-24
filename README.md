# Pipeline de Dados com Python, Google Cloud Functions, BigQuery e Apache Airflow

## Descrição do Projeto

Este projeto implementa um pipeline de dados que realiza extração, transformação, armazenamento e orquestração de informações a partir de uma API pública. A arquitetura serverless escalável permite que o processo funcione automaticamente todos os dias, coletando dados com eficiência e persistindo em um data warehouse para análises posteriores.

## API Utilizada

Para extração dos dados foi utilizada a API pública gratuita ViaCEP, que retorna informações de endereços a partir do CEP.

Exemplo de endpoint:

`https://viacep.com.br/ws/05312903/json/`

## Componentes da Solução

### 1. Extração e Validação de Dados (Python & Cloud Function)

- Um script Python é implementado como Google Cloud Function, executado sob demanda via requisição HTTP.
- A função acessa automaticamente os CEPs cadastrados na tabela `LANDING_API.ceps` no BigQuery.
- Para cada CEP:
  - Realiza uma requisição à API ViaCEP.
  - Valida o retorno e descarta respostas inválidas (como CEPs inexistentes).
  - Os dados válidos são estruturados e enviados para o BigQuery.
- Execução totalmente serverless, escalável e sem necessidade de infraestrutura dedicada.

### `pipeline`

- **Fonte de CEPs**: Tabela BigQuery `LANDING_API.ceps`
- **Fluxo**:
  1. Cria a tabela `endereco_ceps` se ela não existir.
  2. Busca os CEPs do BigQuery.
  3. Requisita dados via API por CEP.
  4. Insere os dados retornados no BigQuery.
  5. Verifica a inserção (checagem com `SELECT COUNT(*)`).

### `pipeline2`

- **Fonte de CEPs**: Variável do Airflow chamada `cep` (em formato JSON)
- **Fluxo**:
  1. Cria a tabela `endereco_ceps` se ela não existir.
  2. Busca os CEPs da variável.
  3. Requisita dados via API por CEP.
  4. Insere os dados no BigQuery.
  5. Verifica se os dados foram inseridos com sucesso.

### 2. Armazenamento de Dados (Google BigQuery)

- **Dataset:** `LANDING_API`
- **Tabelas envolvidas:**
  - `ceps`: armazena os CEPs a serem consultados.
  - `endereco_ceps`: recebe os dados extraídos e validados da API.
- Armazenamento estruturado permite análises, cruzamentos com outras bases e integração com ferramentas analíticas ou modelos preditivos.
- Inserção feita com `insert_rows_json`, respeitando o schema da tabela.

### 3. Orquestração com Apache Airflow

- O pipeline é orquestrado por uma DAG no Apache Airflow.
- **Funcionalidades da DAG:**
  - Aciona a Cloud Function por meio do `HttpOperator`.
  - Verifica se os dados foram carregados corretamente no BigQuery utilizando o `BigQueryCheckOperator` com a seguinte query:

    ```sql
    SELECT COUNT(*) AS total FROM `projetogpc.LANDING_API.endereco_ceps`
    ```

  - A DAG prossegue apenas se o total de registros for maior que zero.
  - Registra logs e erros para monitoramento e auditoria.
  - O agendamento é definido com a expressão cron `0 0 * * *`, executando diariamente à meia-noite.
- A conexão HTTP no Airflow (`google_function_api`) permite integração direta e segura com a Cloud Function.

## Como Executar

### 1. Deploy da Cloud Function

- Configure seu projeto no Google Cloud com faturamento ativado.
- Realize o deploy do script `main.py` como uma Cloud Function com permissão para gravar no BigQuery.
- A função irá:
  - Consultar a tabela `LANDING_API.ceps` no BigQuery.
  - Realizar requisições à API ViaCEP com os CEPs retornados.
  - Inserir os dados retornados na tabela `LANDING_API.endereco_ceps`.

### 2. Configuração do BigQuery

- Crie o dataset `LANDING_API` no BigQuery.
- Crie as seguintes tabelas:
  - `ceps`: tabela com uma coluna `cep` contendo os valores a serem consultados.
  - `endereco_ceps`: tabela de destino com as colunas compatíveis com o retorno da API ViaCEP (ex.: `cep`, `logradouro`, `bairro`, `localidade`, `uf`, etc.).

### 3. Configuração do Airflow

- Configure a conexão HTTP chamada `google_function_api` com:
  - **Host:** URL da Cloud Function (ex.: `https://gcpfunction-xxxx.region.run.app`)
  - **Tipo:** HTTP
  - **Autenticação:** conforme necessário (sem auth ou com headers personalizados).
- Adicione a DAG `pipeline.py` no diretório `dags/` do Airflow.
- Agende a DAG conforme desejado ou execute manualmente. O agendamento `0 0 * * *` executa diariamente à meia-noite.
  
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
│   └── pipeline2.py
├── schemas/                
│   └── schema.py       
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

