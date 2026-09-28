import os
bind='0.0.0.0:8000'
workers=int(os.environ.get('WEB_WORKERS','2'))
worker_class='gthread'
threads=int(os.environ.get('WEB_THREADS','4'))
timeout=30
keepalive=5
max_requests=3000
max_requests_jitter=300
accesslog='-'
errorlog='-'
# El pool se crea por proceso, nunca antes del fork.
preload_app=False

# Run after each worker is initialized. Conditional SQL makes expiry idempotent.
def post_worker_init(worker):
    from app import app, db, start_expiry_worker
    start_expiry_worker(app, db)
