FROM python:3.12

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt


COPY . .


EXPOSE 8501


CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=localhost"]
