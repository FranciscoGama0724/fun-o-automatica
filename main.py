from google.cloud import storage
from google.cloud import bigquery
from datetime import datetime
import uuid
import pytz
import io
from PyPDF2 import PdfReader
from cloudevents.http import CloudEvent
import functions_framework


@functions_framework.cloud_event
def process_file_upload(cloud_event: CloudEvent):
    data = cloud_event.data

    storage_client = storage.Client()
    bigquery_client = bigquery.Client()
    
    bucket_name = data['bucket']
    file_name = data['name']

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(file_name)

    blob.patch()
    print(f'Upload realizado por: {blob.owner}')

    user_id = str(uuid.uuid4())
    user_email = blob.owner['entity'].split('-')[1]
    user_name = user_email.split('@')[0]

    now = datetime.now()
    brazil_tz = now.astimezone(pytz.timezone('America/Sao_Paulo'))
    date = brazil_tz.strftime('%Y-%m-%d %H:%M:%S')
    file_url = f"gs://{bucket_name}/{file_name}"

    # Baixando o PDF como bytes
    pdf_bytes = blob.download_as_bytes()
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))

    # Verifica se o PDF está criptografado
    if pdf_reader.is_encrypted:
        print("O PDF está criptografado. Nenhuma ação será realizada.")
        return

    num_pages = len(pdf_reader.pages)

    INSERT = (f"INSERT INTO `neogov-default.arquivos.relatorios_uploads` VALUES "
              f"('{user_id}', '{user_email}', '{user_name}', '{date}', '{file_url}', {num_pages})")

    bigquery_client.query(INSERT)
    print('Valores salvos na tabela')