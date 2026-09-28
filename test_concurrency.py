"""Prueba HTTP local y aislada. Nunca apunta a un servidor externo."""
import os,tempfile,time,subprocess,sys,json,secrets,statistics,socket
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from datetime import timedelta
from urllib.request import Request,urlopen
from urllib.error import HTTPError
os.environ.pop('DATABASE_URL',None)
_tmp=tempfile.TemporaryDirectory()
os.environ['HOTEL_DATA_DIR']=_tmp.name
os.environ['HOTEL_HTTPS']='0'
from app import app,db,today
with app.app_context():
 for i in range(1,25):db().execute('INSERT INTO users(id,name,email,password) VALUES(?,?,?,?)',(i,'Prueba local',f'c{i}@example.invalid','not-a-login-password'))
 db().commit()
serializer=app.session_interface.get_signing_serializer(app)
def session_headers(i):
 csrf='test-local-'+str(i)
 return {'Content-Type':'application/json','X-CSRF-Token':csrf,'Cookie':'session='+serializer.dumps({'uid':i,'version':0,'csrf':csrf})}
with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
base=f'http://127.0.0.1:{port}'
log=open(Path(_tmp.name)/'server.log','w')
process=subprocess.Popen([sys.executable,'-u','app.py'],cwd=Path(__file__).parent,env={**os.environ,'PORT':str(port)},stdout=log,stderr=log)
def request(path,data=None,i=1):
 started=time.perf_counter();req=Request(base+path,data=json.dumps(data).encode() if data is not None else None,headers=session_headers(i))
 try:
  with urlopen(req,timeout=15) as r:status=r.status;body=json.load(r)
 except HTTPError as e:status=e.code;body=json.load(e)
 return status,body,(time.perf_counter()-started)*1000
try:
 for _ in range(100):
  try:request('/healthz');break
  except Exception:time.sleep(.05)
 else:raise RuntimeError('Servidor local no disponible')
 payload={'room_id':'simple','arrival':(today()+timedelta(days=10)).isoformat(),'departure':(today()+timedelta(days=12)).isoformat(),'guests':1,'phone':'999999999'}
 with ThreadPoolExecutor(max_workers=20) as pool:
  results=list(pool.map(lambda i:request('/api/bookings',{**payload,'request_key':secrets.token_hex(16)},i),range(1,21)))
 counts=Counter(r[0] for r in results)
 assert counts=={201:2,409:18},counts
 with app.app_context():
  rows=db().execute("SELECT unit FROM bookings WHERE room_id='simple' AND status='pendiente'").fetchall()
  assert len(rows)==len({r['unit'] for r in rows})==2
 retry={**payload,'room_id':'doble','request_key':secrets.token_hex(16)}
 with ThreadPoolExecutor(max_workers=5) as pool: retries=list(pool.map(lambda _:request('/api/bookings',retry,21),range(5)))
 assert all(r[0] in (200,201) for r in retries),retries
 assert len({r[1]['id'] for r in retries})==1
 path='/api/availability?arrival='+payload['arrival']+'&departure='+payload['departure']+'&guests=1'
 started=time.perf_counter()
 with ThreadPoolExecutor(max_workers=20) as pool:reads=list(pool.map(lambda _:request(path,i=24),range(200)))
 elapsed=time.perf_counter()-started
 assert all(r[0]==200 for r in reads)
 report={'environment':'Prueba local aislada: Waitress (4 hilos), SQLite, HTTP loopback. No representa capacidad de producción.', 'simultaneous_booking_requests':20,'created':counts[201],'conflicts_correctly_rejected':counts[409],'overbookings':0,'idempotent_retries':5,'reservations_from_retries':1,'availability_requests':200,'availability_concurrency':20,'availability_successes':200,'availability_seconds':round(elapsed,3),'availability_p95_ms':round(sorted(r[2] for r in reads)[189],2),'postgresql_production_tested':False}
 Path(__file__).with_name('RESULTADO_CARGA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps(report,ensure_ascii=False))
finally:
 process.terminate();process.wait(timeout=5);log.close();_tmp.cleanup()
