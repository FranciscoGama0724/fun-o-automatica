# Cloud Run + Eventarc + BigQuery

## Objetivo
Receber uploads de arquivos PDF em um bucket do GCS, registrar cada upload no BigQuery e gerar relatórios diários de uploads por usuário.

## Estrutura
- `main.py`: aplicação Flask que processa eventos de upload
- `cloudbuild.yaml`: CI/CD para Cloud Run
- `relatorio_diario.sql`: query de relatório no BigQuery

## Passos

1. **Crie a tabela no BigQuery** com `relatorio_diario.sql`.
2. **Conceda permissão ao serviço do Cloud Run** para acessar o bucket:
```bash
gsutil iam ch serviceAccount:SEU_EMAIL@...:roles/storage.objectViewer gs://bucket-teste001
```
3. **Crie o gatilho Eventarc**:
```bash
gcloud eventarc triggers create trigger-pdf-upload \
  --location=us-central1 \
  --destination-run-service=fun-o-automatica \
  --destination-run-region=us-central1 \
  --event-filters="type=google.cloud.storage.object.v1.finalized" \
  --event-filters="bucket=bucket-teste001" \
  --service-account=SERVICE_ACCOUNT_DO_EVENTARC
```

4. **Faça deploy via Cloud Build**
Ao dar push na branch `main`, o Cloud Build será acionado automaticamente.
