"""Payments are manually verified; no fake RENIEC or bank verification."""
import os,secrets,json,sqlite3,time
from notifications import enqueue
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from flask import request,session,jsonify,redirect,url_for
from werkzeug.security import check_password_hash,generate_password_hash

def install(app,ctx):
    db=ctx['db']; fail=ctx['fail']; admin=ctx['admin_required']; login=ctx['login_required']; config=ctx['CONFIG']; root=ctx['ROOT']; config_path=ctx['CONFIG_PATH']
    with app.app_context():
        db().execute("CREATE TABLE IF NOT EXISTS notification_outbox(id TEXT PRIMARY KEY,payload TEXT NOT NULL,status TEXT NOT NULL)");db().commit()
        columns={'dni':'TEXT','birthdate':'TEXT','payment_status':"TEXT DEFAULT 'sin informar'",'payment_method':'TEXT','payment_reference':'TEXT','paid_at':'TEXT','verified_by':'INTEGER','receipt_file':'TEXT'}
        if not ctx['POSTGRES']:
            existing={r[1] for r in db().execute('PRAGMA table_info(bookings)')}
            for col,typ in columns.items():
                if col not in existing: db().execute(f'ALTER TABLE bookings ADD COLUMN {col} {typ}')
            users={r[1] for r in db().execute('PRAGMA table_info(users)')}
            if 'must_change' not in users:db().execute('ALTER TABLE users ADD COLUMN must_change INTEGER DEFAULT 0')
            db().commit()
    @app.before_request
    def refresh_config():
        latest=json.loads(config_path.read_text(encoding='utf8'))
        config.update(latest)
    @app.post('/api/email')
    @login
    def email():
        d=request.get_json(); address=ctx['emailval'](d); row=db().execute('SELECT password FROM users WHERE id=?',(session['uid'],)).fetchone()
        if ctx['limited']('email:'+str(session['uid']),8,900): return fail('Espera antes de intentar nuevamente.',429)
        if not check_password_hash(row['password'],d.get('current','')): return fail('Contraseña incorrecta.',403)
        try: db().execute('UPDATE users SET email=? WHERE id=?',(address,session['uid']));db().commit()
        except sqlite3.IntegrityError: return fail('Correo no disponible.',409)
        return jsonify(ok=True)
    @app.post('/api/bookings/<bid>/payment')
    @login
    def payment(bid):
        return fail('Usa el formulario para adjuntar el comprobante.',409)
        d=request.get_json(); ref=ctx['textval'](d,'reference',4,80)
        if d.get('method')!='yape': return fail('Método de pago no habilitado.')
        cur=db().execute("UPDATE bookings SET payment_status='en revisión',payment_method='yape',payment_reference=? WHERE id=? AND user_id=? AND status='pendiente' AND payment_status!='aprobado'",(ref,bid,session['uid']));
        if cur.rowcount:enqueue(db(),bid,'pago informado; pendiente de verificación')
        db().commit()
        if not cur.rowcount:return fail('No puedes modificar el pago de esta reserva.',409)
        return jsonify(ok=True)
    @app.post('/api/admin/payments/<bid>')
    @admin
    def approve(bid):
        if request.get_json().get('verified') is not True:return fail('Confirma la revisión del documento y del abono.')
        cur=db().execute("UPDATE bookings SET payment_status='aprobado',paid_at=?,verified_by=? WHERE id=? AND status IN ('pendiente','confirmada') AND payment_status!='aprobado' AND (payment_status='en revisión' OR payment_method='arrival') AND (arrival_deadline IS NULL OR arrival_deadline>?)",(datetime.now(ZoneInfo('America/Lima')).isoformat(),session['uid'],bid,time.time()));
        if cur.rowcount:enqueue(db(),bid,'pago aprobado por recepción')
        db().commit()
        if not cur.rowcount:return fail('No hay un pago pendiente de revisión.',409)
        return jsonify(ok=True)
    @app.get('/api/admin/metrics')
    @admin
    def metrics():
        now=ctx['today'](); starts={'Hoy':now,'Semana':now-timedelta(days=now.weekday()),'Mes':now.replace(day=1),'Año':now.replace(month=1,day=1)}
        rows=db().execute("SELECT total,paid_at FROM bookings WHERE payment_status='aprobado'").fetchall()
        income={k:sum(r['total'] for r in rows if r['paid_at'] and start.isoformat()<=r['paid_at'][:10]<=now.isoformat()) for k,start in starts.items()}
        top=db().execute("SELECT room_id,COUNT(*) AS n FROM bookings WHERE status IN ('confirmada','completada') GROUP BY room_id ORDER BY n DESC,room_id LIMIT 1").fetchone()
        return jsonify(notifications=[dict(r) for r in db().execute('SELECT id,status FROM notification_outbox ORDER BY id DESC LIMIT 20')],income=income,top_room=next((r['name'] for r in config['rooms'] if top and r['id']==top['room_id']),None))
    @app.post('/api/admin/photo')
    @admin
    def photo():
        from PIL import Image,UnidentifiedImageError
        f=request.files.get('photo'); target=request.form.get('target'); room=next((r for r in config['rooms'] if r['id']==target),None)
        if not f or (target not in ['hero','logo','facade','yape_qr'] and not room):return fail('Selecciona un destino y una imagen.')
        raw=f.read(5*1024*1024+1)
        if len(raw)>5*1024*1024:return fail('Máximo 5 MB.',413)
        import io
        try:
            im=Image.open(io.BytesIO(raw))
            if im.width*im.height>20000000:return fail('Máximo 20 megapíxeles.')
            if im.format not in ['PNG','JPEG','WEBP']:return fail('Usa PNG, JPG o WebP.')
            im.load();im=im.convert('RGB');im.thumbnail((2560,2560))
        except (UnidentifiedImageError,OSError,Image.DecompressionBombError):return fail('Imagen inválida.')
        filename='upload-'+secrets.token_hex(12)+'.png';im.save(root/'static/img'/filename)
        from filelock import FileLock
        with FileLock(str(config_path)+'.lock',timeout=5):
            latest=json.loads(config_path.read_text(encoding='utf8'))
            if room:
                next(r for r in latest['rooms'] if r['id']==target)['image']=filename
            else:latest[target]=filename
            temp=config_path.with_name(config_path.name+'.'+secrets.token_hex(6)+'.tmp')
            temp.write_text(json.dumps(latest,ensure_ascii=False,indent=2),encoding='utf8');temp.replace(config_path)
            config.update(latest)
        return jsonify(ok=True)
    @app.get('/auth/google')
    def google():
        if not os.environ.get('GOOGLE_CLIENT_ID') or not os.environ.get('GOOGLE_CLIENT_SECRET'):return fail('Google todavía no está configurado.',503)
        return oauth.google.authorize_redirect(url_for('google_callback',_external=True))
    @app.get('/auth/google/callback')
    def google_callback():
        if not os.environ.get('GOOGLE_CLIENT_ID'):return fail('Google no configurado.',503)
        token=oauth.google.authorize_access_token();u=token.get('userinfo')
        if not u or not u.get('email_verified'):return fail('Google no verificó el correo.',403)
        email=u['email'].lower();row=db().execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
        if row and row['admin']:return fail('La cuenta administrativa debe usar su contraseña local.',403)
        if not row:
            db().execute('INSERT INTO users(name,email,password) VALUES(?,?,?)',(u.get('name','Huésped')[:80],email,generate_password_hash(secrets.token_urlsafe(48))));db().commit();row=db().execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
        session.clear();session['uid']=row['id'];session['version']=row['session_version'];session['csrf']=secrets.token_hex(32)
        return redirect('/')
    if os.environ.get('GOOGLE_CLIENT_ID') and os.environ.get('GOOGLE_CLIENT_SECRET'):
        from authlib.integrations.flask_client import OAuth
        oauth=OAuth(app);oauth.register(name='google',client_id=os.environ['GOOGLE_CLIENT_ID'],client_secret=os.environ['GOOGLE_CLIENT_SECRET'],server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',client_kwargs={'scope':'openid email profile'})
