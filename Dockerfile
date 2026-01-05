# Usamos a imagem oficial do Playwright que já vem com TODOS os navegadores instalados
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Define a pasta de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . /app

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# O Playwright já está instalado na imagem, não precisamos rodar o install!

# Comando para rodar a aplicação
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
