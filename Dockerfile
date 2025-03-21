# app/Dockerfile

FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    libpangocairo-1.0-0 \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/cibellemc/news-finder.git .

RUN pip install -r requirements.txt

EXPOSE 8507

HEALTHCHECK CMD curl --fail http://localhost:8507/_stcore/health

ENTRYPOINT ["streamlit", "run", "App.py", "--server.port=8507", "--server.address=0.0.0.0"]
