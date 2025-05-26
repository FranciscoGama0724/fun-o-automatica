from flask import Flask, request
from google.cloud import storage, bigquery
from datetime import datetime
import uuid
import pytz
import io
import os
from PyPDF2 import PdfReader

app = Flask(__name__)

@app.route("/", methods=["POST"])
def process_file_upload():
    event_data = request.get_json()

    if not event_data or 'data' not in event_data:
        return "Evento inválido", 400

    data = event_data['data']

    storage_client = storage.Client()
    bigquery_client = bigquery.Client()

    bucket_name = data['bucket']
    file_name = data['name']

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(file_name)

    if not blob:
        return f"Arquivo '{file_name}' não encontrado no bucket '{bucket_name}'", 404

    blob.patch()
    print(f'Upload realizado por: {blob.owner}')

    user_id = str(uuid.uuid4())
    user_email = blob.owner['entity'].split('-')[1]
    user_name = user_email.split('@')[0]

    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
    date = now.strftime('%Y-%m-%d %H:%M:%S')
    file_url = f"gs://{bucket_name}/{file_name}"

    pdf_bytes = blob.download_as_bytes()
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))

    if pdf_reader.is_encrypted:
        print("O PDF está criptografado. Nenhuma ação será realizada.")
        return "PDF criptografado", 200

    num_pages = len(pdf_reader.pages)

    INSERT = (
        f"INSERT INTO `neogov-default.arquivos.relatorios_uploads` "
        f"VALUES ('{user_id}', '{user_email}', '{user_name}', '{date}', '{file_url}', {num_pages})"
    )

    bigquery_client.query(INSERT)
    print('Valores salvos na tabela')

    return "Processamento concluído com sucesso", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
