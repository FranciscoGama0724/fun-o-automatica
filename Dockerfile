# Use imagem oficial do Python
FROM python:3.10-slim

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos do projeto
COPY . .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta esperada pelo Cloud Run
EXPOSE 8080

# Inicia a aplicação Flask usando o functions-framework
CMD ["functions-framework", "--target=app", "--port=8080"]

