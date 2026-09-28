"""Procesa un lote de hasta 30 avisos. Programar cada minuto; no ejecutado durante desarrollo."""
import os,json,re
import requests
from app import app,db
required=['WHATSAPP_TOKEN','WHATSAPP_PHONE_ID','WHATSAPP_TEMPLATE','WHATSAPP_API_VERSION']
if not all(os.environ.get(k) for k in required):raise SystemExit('Falta configurar WhatsApp Business. No se envió ningún mensaje.')
version=os.environ['WHATSAPP_API_VERSION'];phone=os.environ['WHATSAPP_PHONE_ID']
if not re.fullmatch(r'v\d+\.\d+',version) or not phone.isdigit():raise SystemExit('Versión o identificador inválidos.')
with app.app_context():
    rows=db().execute("SELECT id,payload FROM notification_outbox WHERE status='pendiente' ORDER BY id LIMIT 30").fetchall();db().commit()
    for row in rows:
        claimed=db().execute("UPDATE notification_outbox SET status='enviando' WHERE id=? AND status='pendiente'",(row['id'],));db().commit()
        if not claimed.rowcount:continue
        d=json.loads(row['payload'])
        values=[d['id'],d['event'],d['name'],str(d['total']),d['arrival'],d['departure'],d['room_id'],d.get('dni','Sin DNI')]
        payload={'messaging_product':'whatsapp','to':'51939017959','type':'template','template':{'name':os.environ['WHATSAPP_TEMPLATE'],'language':{'code':os.environ.get('WHATSAPP_LANGUAGE','es_PE')},'components':[{'type':'body','parameters':[{'type':'text','text':v} for v in values]}]}}
        try:
            response=requests.post(f'https://graph.facebook.com/{version}/{phone}/messages',headers={'Authorization':'Bearer '+os.environ['WHATSAPP_TOKEN']},json=payload,timeout=15)
            status='aceptado por Meta' if response.ok and response.json().get('messages') else 'fallido'
        except (requests.RequestException,ValueError):status='incierto'
        db().execute('UPDATE notification_outbox SET status=? WHERE id=?',(status,row['id']));db().commit()
        print(row['id'],status)
