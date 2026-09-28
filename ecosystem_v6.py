"""Room editor, private stay reports and one-hour arrival deadlines."""
import json,re,secrets,time,threading
from flask import request,jsonify,session,Response
from filelock import FileLock

def expire(con,now=None):
    now=time.time() if now is None else now
    con.execute("UPDATE bookings SET status='libre' WHERE status IN ('pendiente','confirmada') AND arrival_deadline IS NOT NULL AND arrival_deadline<=? AND payment_status!='aprobado'",(now,))
    con.commit()

def start_expiry_worker(app,db):
    def work():
        while True:
            try:
                with app.app_context(): expire(db())
            except Exception: app.logger.exception('No se pudo procesar un vencimiento; se reintentará.')
            time.sleep(15)
    threading.Thread(target=work,name='reservation-expiry',daemon=True).start()

def customer_bookings(con,uid,today,config=None):
    # Explicit allowlist: birth date / verification / internal data never leave to customer.
    rows=con.execute("SELECT id,room_id,arrival,departure,guests,total,status,payment_status,payment_method,receipt_file,arrival_deadline,room_report FROM bookings WHERE user_id=? AND status IN ('pendiente','confirmada') AND departure>? ORDER BY created DESC",(uid,today.isoformat())).fetchall()
    result=[]
    for row in rows:
        b=dict(row);b['receipt_file']=bool(b['receipt_file'])
        if config:
            from public_catalog import public_room
            room=next((r for r in config['rooms'] if r['id']==b['room_id']),None)
            if room:
                # The public/customer API never exposes the internal room number.
                # The customer receives it only after their own reservation is confirmed and paid.
                b['room_id']=public_room(room)['id']
        raw=b.pop('room_report',None)
        b['report']=json.loads(raw) if raw and b['status']=='confirmada' and b['payment_status']=='aprobado' else None
        if b['report']:
            b['assigned_number']=b['report'].get('number')
        result.append(b)
    return result

def install_ecosystem(app,ctx):
    db=ctx['db'];admin=ctx['admin_required'];fail=ctx['fail'];config=ctx['CONFIG'];path=ctx['CONFIG_PATH']
    with app.app_context():
        if not ctx['POSTGRES']:
            columns={r[1] for r in db().execute('PRAGMA table_info(bookings)')}
            for key,kind in {'arrival_deadline':'REAL','identity_checked':'INTEGER DEFAULT 0','room_report':'TEXT'}.items():
                if key not in columns:db().execute(f'ALTER TABLE bookings ADD COLUMN {key} {kind}')
            db().execute('CREATE INDEX IF NOT EXISTS expiry_deadlines ON bookings(arrival_deadline,status)');db().commit()
    @app.before_request
    def expire_requests():
        if request.path.startswith('/api/'): expire(db())
    def save(change):
        with FileLock(str(path)+'.lock',timeout=5):
            latest=json.loads(path.read_text(encoding='utf8'));change(latest)
            tmp=path.with_name(path.name+'.'+secrets.token_hex(8)+'.tmp')
            tmp.write_text(json.dumps(latest,ensure_ascii=False,indent=2),encoding='utf8');tmp.replace(path);config.update(latest)
    @app.post('/api/admin/rooms/<rid>')
    @admin
    def edit_room(rid):
        d=request.get_json();out={}
        for field,limit in {'name':100,'number':3,'beds':100,'category':50,'description':1500,'floor':30,'side':80,'window':100,'directions':1000}.items():
            out[field]=ctx['textval'](d,field,1,limit)
        if not re.fullmatch(r'[0-9]{3}',out['number']):return fail('Usa tres dígitos para el número de habitación.')
        for key,lo,hi in [('price',1,10000),('capacity',1,4),('size',1,500)]:
            value=d.get(key)
            if type(value) is not int or not lo<=value<=hi:return fail('Valor inválido: '+key)
            out[key]=value
        if not isinstance(d.get('features'),list) or not 1<=len(d['features'])<=20 or any(not isinstance(x,str) or not 1<=len(x.strip())<=80 for x in d['features']):return fail('Introduce de 1 a 20 servicios, hasta 80 caracteres cada uno.')
        out['features']=[x.strip() for x in d['features']]
        for key in ['active','example']:
            if not isinstance(d.get(key),bool):return fail('Revisa '+key)
            out[key]=d[key]
        def change(latest):
            target=next((r for r in latest['rooms'] if r['id']==rid),None)
            if not target:raise ValueError('Habitación no encontrada.')
            if any(r['id']!=rid and r['number']==out['number'] for r in latest['rooms']):raise ValueError('Este número ya pertenece a otra habitación.')
            target.update(out)
        save(change);return jsonify(ok=True)
    @app.post('/api/admin/site')
    @admin
    def edit_site():
        d=request.get_json();fields={'name':100,'tagline':150,'address':300,'city':100,'phone':30,'whatsapp':15,'checkin':5,'checkout':5,'hero_title':100,'hero_text':400,'about_title':100,'about_text':1500}
        out={k:ctx['textval'](d,k,1,n) for k,n in fields.items()}
        if not re.fullmatch(r'[0-9]{8,15}',out['whatsapp']):return fail('WhatsApp: código de país y número, solo dígitos.')
        for k in ['checkin','checkout']:
            if not re.fullmatch(r'(?:[01][0-9]|2[0-3]):[0-5][0-9]',out[k]):return fail('Usa horas HH:MM.')
        save(lambda latest:latest.update(out));return jsonify(ok=True)
    @app.get('/api/bookings/<bid>/report')
    @ctx['login_required']
    def report(bid):
        b=next((b for b in customer_bookings(db(),session['uid'],ctx['today']()) if b['id']==bid),None)
        if not b or not b['report']:return fail('El informe estará disponible con la reserva y el pago aprobados.',404)
        r=b['report']
        body=f"{config['name']}\nRESERVA CONFIRMADA · {bid}\n\nDirección: {config['address']}\nHabitación: {r['number']} · {r['name']}\nPiso: {r['floor']}\nLado: {r['side']}\nVentana: {r['window']}\nCamas: {r['beds']}\nServicios: {', '.join(r['features'])}\nCómo llegar a tu habitación: {r['directions']}\n\nIngreso: {b['arrival']} · {config['checkin']}\nSalida: {b['departure']} · {config['checkout']}\nPago aprobado: S/ {b['total']}\nPresenta tu documento original en recepción."
        return Response(body,content_type='text/plain; charset=utf-8',headers={'Content-Disposition':f'attachment; filename="Informe-{bid}.txt"'})
