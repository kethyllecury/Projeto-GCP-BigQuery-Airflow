from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.http.hooks.http import HttpHook
from airflow.providers.google.cloud.operators.bigquery import BigQueryCheckOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryCreateEmptyTableOperator
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from datetime import datetime
from schemas.schema import schema
import time

def ler_ceps_do_bigquery(**kwargs):
    ti = kwargs['ti']
    hook = BigQueryHook(gcp_conn_id='google_cloud_default', use_legacy_sql=False)
    sql = "SELECT cep FROM `projetogpc.LANDING_API.ceps`"
    conn = hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(sql)
    ceps = [row[0] for row in cursor.fetchall()]
    ti.xcom_push(key='lista_ceps', value=ceps)

def requisitar_por_cep(**kwargs):
    ti = kwargs['ti']
    ceps = ti.xcom_pull(task_ids='buscar_ceps_bigquery', key='lista_ceps')
    http = HttpHook(method='GET', http_conn_id='google_function_api')

    dados_ceps = []
    campos_esperados = {f['name'] for f in schema}

    for cep in ceps:
        try:
            resp = http.run(f"acessar_cep/?cep={cep}")
            if resp.status_code == 200:
                data = resp.json()
                registro = {campo: data.get(campo) for campo in campos_esperados}
                registro['cep'] = cep 
                dados_ceps.append(registro)
            else:
                pass
        except Exception as e:
            pass

    ti.xcom_push(key='dados_ceps', value=dados_ceps)

def inserir_dados_no_bigquery(**kwargs):
    ti = kwargs['ti']
    dados_ceps = ti.xcom_pull(task_ids='requisitar_por_cep', key='dados_ceps')
    
    campos_esperados = {f['name'] for f in schema}
    dados_filtrados = [
        {campo: registro.get(campo) for campo in campos_esperados}
        for registro in dados_ceps
    ]

    hook = BigQueryHook(gcp_conn_id='google_cloud_default', use_legacy_sql=False)
    client = hook.get_client(project_id='projetogpc')
    table_ref = client.dataset('LANDING_API').table('endereco_ceps')
    errors = client.insert_rows_json(table=table_ref, json_rows=dados_filtrados)

    if errors:
        raise ValueError(f"Erro ao inserir linhas: {errors}")

with DAG(
    dag_id="pipeline",
    start_date=datetime(2025, 1, 1),
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

    buscar_ceps_bigquery = PythonOperator(
        task_id='buscar_ceps_bigquery',
        python_callable=ler_ceps_do_bigquery,
    )

    requisitar_ceps = PythonOperator(
        task_id="requisitar_por_cep",
        python_callable=requisitar_por_cep,
    )

    inserir = PythonOperator(
        task_id='inserir_dados_bigquery',
        python_callable=inserir_dados_no_bigquery,
    )

    verificar_bigquery = BigQueryCheckOperator(
        task_id="consultar_cep_bigquery",
        sql='SELECT COUNT(*) as total FROM `projetogpc.LANDING_API.endereco_ceps`',
        use_legacy_sql=False,
        location='southamerica-east1',
    )

    criar_tabela >>buscar_ceps_bigquery >> requisitar_ceps >> inserir >> verificar_bigquery
