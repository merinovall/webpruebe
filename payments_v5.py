import io,secrets,os,time
from pathlib import Path
from urllib.parse import quote
from flask import request,session,jsonify,send_file,render_template,redirect
from PIL import Image,UnidentifiedImageError
from notifications import enqueue

def install_payments(app,ctx):
 db=ctx['db'];fail=ctx['fail'];login=ctx['login_required'];admin=ctx['admin_required'];data=ctx['DATA'];config=ctx['CONFIG']
 receipts=data/'receipts';receipts.mkdir(exist_ok=True)
 def own(bid):
  return db().execute('SELECT b.*,u.name FROM bookings b JOIN users u ON u.id=b.user_id WHERE b.id=? AND b.user_id=?',(bid,session['uid'])).fetchone()
 def result(row,event):
  text=f"{event}\nCliente: {row['name']}\nDNI: {row['dni']}\nReserva: {row['id']}\nHabitación: {row['room_id']}\nIngreso: {row['arrival']}\nSalida: {row['departure']}\nTotal: S/ {row['total']}\nPendiente de revisión por recepción."
  configured=all(os.environ.get(k) for k in ['WHATSAPP_TOKEN','WHATSAPP_PHONE_ID','WHATSAPP_TEMPLATE','WHATSAPP_API_VERSION'])
  return jsonify(message='Solicitud registrada. Aviso en cola para WhatsApp.' if configured else 'Solicitud registrada en recepción. WhatsApp automático aún no está conectado.',whatsapp_url='https://wa.me/51939017959?text='+quote(text))
 @app.post('/api/bookings/<bid>/pay-arrival')
 @login
 def pay_arrival(bid):
  row=own(bid)
  if not row:return fail('Reserva no disponible.',404)
  if row['payment_method']=='arrival' and row['status']=='pendiente':return result(row,'Reserva con pago al llegar')
  cur=db().execute("UPDATE bookings SET payment_method='arrival',payment_status='pago al llegar',arrival_deadline=? WHERE id=? AND user_id=? AND status='pendiente' AND payment_status='sin informar'",(time.time()+3600,bid,session['uid']))
  if not cur.rowcount:db().rollback();return fail('Ya hay un pago en revisión o una decisión de recepción. Contacta con el hospedaje.',409)
  enqueue(db(),bid,'reserva solicitada con pago al llegar');db().commit();return result(row,'Reserva con pago al llegar')
 @app.route('/api/bookings/<bid>/receipt',methods=['GET','POST'])
 @login
 def receipt(bid):
  row=db().execute('SELECT b.*,u.name FROM bookings b JOIN users u ON u.id=b.user_id WHERE b.id=?',(bid,)).fetchone()
  user=db().execute('SELECT admin FROM users WHERE id=?',(session['uid'],)).fetchone()
  if not row or (row['user_id']!=session['uid'] and not user['admin']):return fail('Comprobante no disponible.',404)
  if request.method=='GET':
   if not row['receipt_file']:return fail('No hay comprobante.',404)
   return send_file(receipts/row['receipt_file'],mimetype='image/png',download_name='comprobante.png',max_age=0)
  if row['user_id']!=session['uid']:return fail('Solo el titular puede enviar el comprobante.',403)
  if ctx['limited']('receipt:'+str(session['uid']),10,3600):return fail('Demasiados envíos. Intenta más tarde.',429)
  f=request.files.get('receipt');ref=request.form.get('reference','').strip()
  if len(ref)>80:return fail('La referencia admite hasta 80 caracteres.')
  if not f:return fail('Adjunta el comprobante.')
  raw=f.read(5*1024*1024+1)
  if len(raw)>5*1024*1024:return fail('Máximo 5 MB.',413)
  try:
   im=Image.open(io.BytesIO(raw))
   if im.format not in ['PNG','JPEG','WEBP'] or im.width*im.height>20000000:return fail('Usa una imagen JPG, PNG o WebP de hasta 20 megapíxeles.')
   im.load();im=im.convert('RGB');im.thumbnail((2400,2400))
  except (UnidentifiedImageError,OSError,Image.DecompressionBombError):return fail('Imagen no válida.')
  filename=secrets.token_hex(24)+'.png';path=receipts/filename;im.save(path)
  try:
   cur=db().execute("UPDATE bookings SET receipt_file=?,payment_reference=?,payment_method='yape',payment_status='en revisión' WHERE id=? AND user_id=? AND status='pendiente' AND payment_status IN ('sin informar','en revisión','pago al llegar') AND (arrival_deadline IS NULL OR arrival_deadline>?)",(filename,ref,bid,session['uid'],time.time()))
   if not cur.rowcount:db().rollback();path.unlink(missing_ok=True);return fail('La reserva ya no admite comprobantes.',409)
   enqueue(db(),bid,'comprobante recibido; pago NO verificado');db().commit()
  except Exception:db().rollback();path.unlink(missing_ok=True);raise
  return result(row,'Comprobante recibido, pendiente de verificar')
 @app.get('/admin')
 def admin_page():
  row=db().execute('SELECT admin,must_change FROM users WHERE id=?',(session.get('uid',-1),)).fetchone()
  if not row or not row['admin'] or row['must_change']:return redirect('/')
  response=app.make_response(render_template('admin.html',hotel=config));response.headers['Cache-Control']='no-store';return response
 @app.get('/api/admin/overview')
 @admin
 def overview():
  from datetime import timedelta
  now=ctx['today']();a=now.isoformat();b=(now+timedelta(days=1)).isoformat()
  occupied=db().execute("SELECT COUNT(DISTINCT room_id) FROM bookings WHERE status IN ('confirmada','completada') AND arrival<=? AND departure>?",(a,a)).fetchone()[0]
  arrivals=db().execute("SELECT COUNT(*) FROM bookings WHERE status='confirmada' AND arrival=?",(a,)).fetchone()[0]
  series=[]
  for i in range(13,-1,-1):
   d=(now-timedelta(days=i)).isoformat();rows=db().execute("SELECT total FROM bookings WHERE payment_status='aprobado' AND paid_at>=? AND paid_at<?",(d,(now-timedelta(days=i-1)).isoformat())).fetchall();series.append({'day':d,'total':sum(r['total'] for r in rows)})
  return jsonify(occupied=occupied,rooms=len(config['rooms']),arrivals=arrivals,series=series)
