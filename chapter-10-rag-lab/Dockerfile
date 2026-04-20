FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md main.py /app/
COPY rag_lab /app/rag_lab
COPY data /app/data
COPY docs /app/docs

RUN pip install --no-cache-dir .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
