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
    data = event_data.get("message", {}).get("attributes", {})

    bucket_name = data.get("bucketId") or data.get("bucket")
    file_name = data.get("objectId") or data.get("name")

    if not bucket_name or not file_name:
        return "Dados de evento inválidos", 400

    storage_client = storage.Client()
    bigquery_client = bigquery.Client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.get_blob(file_name)

    if not blob:
        return f"Arquivo '{file_name}' não encontrado em '{bucket_name}'", 404

    user_email = blob.owner.get('entity', 'unknown-user').split('-')[-1]
    user_name = user_email.split('@')[0] if '@' in user_email else user_email
    user_id = str(uuid.uuid4())

    now = datetime.now(pytz.timezone('America/Sao_Paulo'))
    date = now.strftime('%Y-%m-%d %H:%M:%S')
    file_url = f"gs://{bucket_name}/{file_name}"

    pdf_bytes = blob.download_as_bytes()
    pdf_reader = PdfReader(io.BytesIO(pdf_bytes))

    if pdf_reader.is_encrypted:
        return "PDF criptografado", 200

    num_pages = len(pdf_reader.pages)

    query = f"""
    INSERT INTO `neogov-default.arquivos.relatorios_uploads`
    (user_id, user_email, user_name, date, file_url, num_pages)
    VALUES (
        '{user_id}', '{user_email}', '{user_name}', '{date}', '{file_url}', {num_pages}
    )
    """

    bigquery_client.query(query)

    return "Registro salvo no BigQuery com sucesso", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
