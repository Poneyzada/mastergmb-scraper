# Imagem oficial da Microsoft que já vem com Python e TODOS os navegadores instalados
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Pasta de trabalho no servidor
WORKDIR /app

# Copia os arquivos do seu GitHub para dentro do servidor
COPY . /app

# Instala as bibliotecas (FastAPI, Uvicorn, etc)
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta que o servidor vai usar
EXPOSE 8080

# Comando para rodar a aplicação usando a porta dinâmica do Railway
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}"]
