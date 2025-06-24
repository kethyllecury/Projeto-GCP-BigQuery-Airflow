from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyTableOperator
from airflow.operators.python import PythonOperator
from airflow.providers.http.hooks.http import HttpHook
from google.cloud import bigquery
from airflow.models import Variable
from datetime import datetime
from schemas.schema import schema

def buscar_variavel_cep():
    ceps = Variable.get("cep", deserialize_json=True)
    return ceps 

def requisitar_por_cep(ti):
    ceps = ti.xcom_pull(task_ids='buscar_cep', key='return_value') 
    http = HttpHook(method="GET", http_conn_id="google_function_api")
    campos_esperados = {f['name'] for f in schema}
    dados_ceps = []

    for cep in ceps:
        try:
            endpoint = f"acessar_cep/?cep={cep}"
            response = http.run(endpoint)
            if response.status_code == 200:
                data = response.json()
                registro = {campo: data.get(campo) for campo in campos_esperados}
                registro['cep'] = cep  
                dados_ceps.append(registro)
        except Exception:
            pass

    ti.xcom_push(key='dados_ceps', value=dados_ceps)

def inserir_dados_no_bigquery(ti):
    dados_ceps = ti.xcom_pull(task_ids='requisitar_por_cep', key='dados_ceps')

    campos_esperados = {f['name'] for f in schema}
    dados_filtrados = [
        {campo: registro.get(campo) for campo in campos_esperados}
        for registro in dados_ceps
    ]

    client = bigquery.Client(project='projetogpc')
    table_id = "projetogpc.LANDING_API.endereco_ceps"
    client.insert_rows_json(table_id, dados_filtrados)

with DAG(
    dag_id="pipeline2",
    start_date=datetime(2025, 6, 22),
    schedule='@daily',
    catchup=False
) as dag:
    
    criar_tabela = BigQueryCreateEmptyTableOperator(
        task_id="criar_tabela_bigquery",
        project_id="projetogpc",
        dataset_id="LANDING_API",
        table_id="endereco_ceps",
        schema_fields=schema,
        location="southamerica-east1",
        exists_ok=True,
    )

    buscar_cep = PythonOperator(
        task_id="buscar_cep",
        python_callable=buscar_variavel_cep
    )
    
    requisitar_por_cep_task = PythonOperator(
        task_id="requisitar_por_cep",
        python_callable=requisitar_por_cep
    )
    
    inserir_dados = PythonOperator(
        task_id="inserir_dados_no_bigquery",
        python_callable=inserir_dados_no_bigquery
    )
    
    verificar_cep_bigquery = BigQueryCheckOperator(
        task_id="verificar_bigquery_cep", 
        sql="SELECT COUNT(*) as total FROM `projetogpc.LANDING_API.endereco_ceps`",
        use_legacy_sql=False,
        location='southamerica-east1'
    )
    
    criar_tabela >> buscar_cep >> requisitar_por_cep_task >> inserir_dados >> verificar_cep_bigquery
