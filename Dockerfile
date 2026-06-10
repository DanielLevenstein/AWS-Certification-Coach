FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=8501

WORKDIR /app

COPY pyproject.toml README.md requirements.txt ./
COPY src ./src
RUN pip install --no-cache-dir -e .

COPY app.py ./
COPY config ./config
COPY data ./data
COPY models ./models

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8501/_stcore/health').read()"

CMD ["streamlit", "run", "app.py"]
