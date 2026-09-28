import threading, webbrowser, os
from waitress import serve
from app import app,db,start_expiry_worker
start_expiry_worker(app,db)
port=int(os.environ.get('PORT','5000'))
threading.Timer(1.5,lambda:webbrowser.open(f'http://127.0.0.1:{port}')).start()
print(f'Hospedaje Río Negro: http://127.0.0.1:{port}')
print('Mantén esta ventana abierta. Pulsa Ctrl+C para detener el servidor.')
serve(app,host='127.0.0.1',port=port)
