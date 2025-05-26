FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT=8080

CMD ["functions-framework", "--target=process_file_upload", "--port=8080"]