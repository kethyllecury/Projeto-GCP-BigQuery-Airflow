# https://airflow.apache.org/docs/docker-stack/build.html
FROM apache/airflow:3.0.1
COPY requirements.txt /
RUN pip install --no-cache-dir -r /requirements.txt
