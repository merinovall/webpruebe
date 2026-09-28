FROM python:3.12-slim
WORKDIR /app
COPY requirements*.txt ./
RUN pip install --no-cache-dir -r requirements-production.txt && useradd --create-home hotel
COPY . .
RUN mkdir -p /app/instance && chown -R hotel:hotel /app
USER hotel
EXPOSE 8000
CMD ["gunicorn","--config","deploy/gunicorn.conf.py","app:app"]
