FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .
# Templates are inline in server.py (no separate templates directory needed)

EXPOSE 9090

HEALTHCHECK --interval=15s --timeout=5s --retries=3 --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9090/health')" || exit 1

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "9090"]
