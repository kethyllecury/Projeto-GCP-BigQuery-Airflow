from airflow import DAG
from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator
from datetime import datetime

with DAG(
    dag_id="pipeline",
    start_date=datetime(2025, 1, 1),
    schedule='@daily',
    catchup=False,
) as dag:
    
    ativar_funcao = HttpOperator(
        task_id="ativar_cloud_function",
        method="GET",
        http_conn_id="google_function_api",
        endpoint="acessar_cep",    
        headers={"Content-Type": "application/json"},
        log_response=True)

    verificar_bigquery = BigQueryCheckOperator(
        task_id="consultar_cep_bigquery",
        sql='select count(*) as total FROM `projetogpc.LANDING_API.endereco_ceps`',
        use_legacy_sql=False,
        location='southamerica-east1')

    ativar_funcao >> verificar_bigquery 
