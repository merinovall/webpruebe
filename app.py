from public_catalog import public_room,public_hotel
"""Hospedaje Río Negro — Flask + SQLite. Ejecutar: python app.py."""
import os, json, sqlite3, secrets, re, functools, getpass, sys
from pathlib import Path
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from flask import Flask, request, session, jsonify, render_template, g
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException
from notifications import enqueue
from database import POSTGRES,connect,lock_room,init_postgres,BusyDatabase
ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get('HOTEL_DATA_DIR', ROOT / 'instance'))
DATA.mkdir(parents=True, exist_ok=True)
if POSTGRES and len(os.environ.get('SECRET_KEY',''))<32: raise RuntimeError('Configura SECRET_KEY compartida, de al menos 32 caracteres, para PostgreSQL.')
secretfile = DATA / 'secret.key'
if not secretfile.exists():
    try:
        fd = os.open(secretfile, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(fd, 'w') as f: f.write(secrets.token_hex(32))
    except FileExistsError: pass
app = Flask(__name__)
app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or secretfile.read_text(), MAX_CONTENT_LENGTH=6*1024*1024,
    SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', SESSION_COOKIE_SECURE=os.environ.get('HOTEL_HTTPS')=='1',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=8))
CONFIG_PATH=Path(os.environ.get('HOTEL_CONFIG_FILE',ROOT/'hotel.json'))
if not CONFIG_PATH.exists():
    CONFIG_PATH.parent.mkdir(parents=True,exist_ok=True)
    try:
        with CONFIG_PATH.open('x',encoding='utf8') as f:f.write((ROOT/'hotel.json').read_text(encoding='utf8'))
    except FileExistsError:pass
CONFIG = json.loads(CONFIG_PATH.read_text(encoding='utf-8'))
def today(): return datetime.now(ZoneInfo('America/Lima')).date()
def db():
    if 'db' not in g:
        g.db=connect(DATA)
    return g.db
@app.teardown_appcontext
def close_db(error=None):
    con=g.pop('db',None)
    if con: con.close()
def init():
    if POSTGRES:
        init_postgres()
        return
    with app.app_context():
        db().executescript('''
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password TEXT NOT NULL,admin INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS bookings(id TEXT PRIMARY KEY,user_id INTEGER REFERENCES users(id),room_id TEXT,unit INTEGER,arrival TEXT,departure TEXT,guests INTEGER,total INTEGER,status TEXT DEFAULT 'pendiente',phone TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE INDEX IF NOT EXISTS booking_dates ON bookings(room_id,arrival,departure,status);
        CREATE TABLE IF NOT EXISTS reviews(id INTEGER PRIMARY KEY,user_id INTEGER UNIQUE REFERENCES users(id),rating INTEGER CHECK(rating BETWEEN 1 AND 5),body TEXT,approved INTEGER DEFAULT 0,created TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY,name TEXT,email TEXT,body TEXT,created TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS attempts(key TEXT PRIMARY KEY,count INTEGER,expires REAL);
        ''')
        columns={r[1] for r in db().execute('PRAGMA table_info(users)')}
        if 'session_version' not in columns: db().execute('ALTER TABLE users ADD COLUMN session_version INTEGER DEFAULT 0')
        booking_columns={r[1] for r in db().execute('PRAGMA table_info(bookings)')}
        if 'request_key' not in booking_columns: db().execute('ALTER TABLE bookings ADD COLUMN request_key TEXT')
        db().execute('CREATE UNIQUE INDEX IF NOT EXISTS booking_retry ON bookings(user_id,request_key)')
        db().execute('CREATE INDEX IF NOT EXISTS booking_user ON bookings(user_id,created DESC)')
        db().commit()
def fail(message,code=400): return jsonify(error=message),code
def login_required(fn):
    @functools.wraps(fn)
    def inner(*a,**kw):
        if not session.get('uid'): return fail('Inicia sesión para continuar.',401)
        return fn(*a,**kw)
    return inner
def admin_required(fn):
    @functools.wraps(fn)
    @login_required
    def inner(*a,**kw):
        row=db().execute('SELECT admin FROM users WHERE id=?',(session['uid'],)).fetchone()
        if not row or not row['admin']: return fail('No tienes acceso a esta sección.',403)
        return fn(*a,**kw)
    return inner
def textval(data,key,lo=1,hi=200):
    val=data.get(key,'')
    if not isinstance(val,str) or not lo<=len(val.strip())<=hi: raise ValueError('Revisa el campo '+key+'.')
    return val.strip()
def emailval(data):
    val=textval(data,'email',5,254).lower()
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',val): raise ValueError('Escribe un correo válido.')
    return val
def limited(key,limit,seconds):
    import time
    now=time.time(); con=db()
    key=key+':'+(request.remote_addr or 'local')
    con.execute('INSERT INTO attempts VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET count=CASE WHEN attempts.expires < ? THEN 1 ELSE attempts.count+1 END, expires=CASE WHEN attempts.expires < ? THEN ? ELSE attempts.expires END',(key,now+seconds,now,now,now+seconds))
    count=con.execute('SELECT count FROM attempts WHERE key=?',(key,)).fetchone()[0]; con.commit()
    return count>limit
@app.before_request
def guard():
    if (request.path.startswith('/api/') or request.path=='/admin') and session.get('uid'):
        row=db().execute('SELECT session_version FROM users WHERE id=?',(session['uid'],)).fetchone()
        if not row or session.get('version')!=row['session_version']: session.clear()
        if session.get('uid') and request.path not in ['/api/bootstrap','/api/password','/api/logout']:
            flags=db().execute('SELECT must_change FROM users WHERE id=?',(session['uid'],)).fetchone()
            if flags and flags['must_change']: return fail('Cambia la contraseña inicial antes de continuar.',403)
    if request.path.startswith('/api/') and request.method not in ('GET','HEAD','OPTIONS'):
        token=session.get('csrf','')
        if not token or not secrets.compare_digest(token,request.headers.get('X-CSRF-Token','')): return fail('Tu sesión cambió. Recarga la página.',403)
        if request.path=='/api/admin/photo' or (request.path.startswith('/api/bookings/') and request.path.endswith('/receipt')): return
        if request.content_length and request.content_length>16384: return fail('Solicitud demasiado grande.',413)
        if not request.is_json: return fail('Se requiere JSON.',415)
        if not isinstance(request.get_json(silent=True),dict): return fail('Solicitud inválida.')
@app.after_request
def headers(response):
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    response.headers['Permissions-Policy']='camera=(), microphone=(), geolocation=()'
    response.headers['X-DNS-Prefetch-Control']='off'
    response.headers['Cross-Origin-Resource-Policy']='same-origin'
    response.headers['Cross-Origin-Opener-Policy']='same-origin'
    response.headers['Content-Security-Policy']="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; media-src 'self'; frame-src https://www.google.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
    if request.path.startswith('/api/'): response.headers['Cache-Control']='no-store'
    if app.config['SESSION_COOKIE_SECURE']: response.headers['Strict-Transport-Security']='max-age=31536000'
    return response
@app.errorhandler(ValueError)
def bad_value(e): return fail(str(e))
@app.errorhandler(HTTPException)
def http_error(e): return fail('Solicitud no disponible.' if e.code==404 else e.description,e.code)
@app.errorhandler(Exception)
def internal(e):
    app.logger.exception('Error de aplicación')
    return fail('No se pudo completar la operación. Inténtalo nuevamente.',500)
@app.get('/')
def index(): return render_template('index.html',hotel=public_hotel(CONFIG))
@app.get('/api/bootstrap')
def bootstrap():
    session.setdefault('csrf',secrets.token_hex(32)); session.permanent=True
    user=db().execute('SELECT id,name,email,admin,must_change FROM users WHERE id=?',(session['uid'],)).fetchone() if session.get('uid') else None
    return jsonify(hotel=CONFIG if user and user['admin'] else public_hotel(CONFIG),user=dict(user) if user else None,csrf=session['csrf'],today=today().isoformat(),google_enabled=bool(os.environ.get('GOOGLE_CLIENT_ID') and os.environ.get('GOOGLE_CLIENT_SECRET')))
@app.post('/api/register')
def register():
    if limited('register',8,3600): return fail('Demasiados intentos. Intenta más tarde.',429)
    data=request.get_json(); name=textval(data,'name',2,80); email=emailval(data); password=textval(data,'password',10,128)
    if data.get('consent') is not True: return fail('Acepta la política de privacidad para crear tu cuenta.')
    try:
        cur=db().execute('INSERT INTO users(name,email,password) VALUES(?,?,?)',(name,email,generate_password_hash(password)))
        db().commit()
    except sqlite3.IntegrityError: return fail('No se pudo crear la cuenta con ese correo. Intenta iniciar sesión.',409)
    session.clear(); session['uid']=cur.lastrowid; session['version']=0; session['csrf']=secrets.token_hex(32)
    return bootstrap()
@app.post('/api/login')
def login():
    data=request.get_json(); email=emailval(data)
    if limited('login:'+email,10,900) or limited('login-all',50,900): return fail('Demasiados intentos. Espera 15 minutos.',429)
    row=db().execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
    password=textval(data,'password',1,128)
    if not check_password_hash(row['password'] if row else DUMMY_HASH,password): return fail('Correo o contraseña incorrectos.',401)
    session.clear(); session['uid']=row['id']; session['version']=row['session_version']; session['csrf']=secrets.token_hex(32)
    return bootstrap()
@app.post('/api/logout')
def logout(): session.clear(); return jsonify(ok=True)
@app.post('/api/password')
@login_required
def password():
    data=request.get_json(); old=textval(data,'current',1,128); new=textval(data,'password',10,128)
    row=db().execute('SELECT password FROM users WHERE id=?',(session['uid'],)).fetchone()
    if limited('password:'+str(session['uid']),8,900): return fail('Espera 15 minutos.',429)
    if not check_password_hash(row['password'],old): return fail('La contraseña actual es incorrecta.')
    db().execute('UPDATE users SET password=?,must_change=0,session_version=session_version+1 WHERE id=?',(generate_password_hash(new),session['uid'])); db().commit()
    session.clear(); return jsonify(ok=True)
def dates(data):
    try:
        arrival=date.fromisoformat(data.get('arrival','')); departure=date.fromisoformat(data.get('departure','')); guests=int(data.get('guests',0))
    except (ValueError,TypeError): raise ValueError('Selecciona fechas y huéspedes válidos.')
    if arrival<today() or departure<=arrival or (departure-arrival).days>30 or arrival>today()+timedelta(days=365): raise ValueError('Elige una estancia de 1 a 30 noches, dentro de los próximos 12 meses.')
    if guests not in range(1,5): raise ValueError('Selecciona de 1 a 4 huéspedes.')
    return arrival.isoformat(),departure.isoformat(),guests,(departure-arrival).days
def free_units(room,a,b):
    taken={r[0] for r in db().execute("SELECT unit FROM bookings WHERE room_id=? AND status IN ('pendiente','confirmada') AND arrival < ? AND departure > ?",(room['id'],b,a))}
    return [n for n in range(1,room['units']+1) if n not in taken]
@app.get('/api/availability')
def availability():
    a,b,guests,nights=dates(request.args)
    admin_view=db().execute('SELECT admin FROM users WHERE id=?',(session.get('uid',-1),)).fetchone()
    return jsonify(rooms=[dict(r if admin_view and admin_view['admin'] else public_room(r),available=len(free_units(r,a,b)),total=r['price']*nights) for r in CONFIG['rooms'] if r.get('active',True) and r['capacity']>=guests],nights=nights)
@app.route('/api/bookings',methods=['GET','POST'])
@login_required
def bookings():
    if request.method=='GET': return jsonify(bookings=customer_bookings(db(),session['uid'],today(),CONFIG))
    data=request.get_json(); a,b,guests,nights=dates(data); dni=textval(data,'dni',8,8)
    if not re.fullmatch(r'[0-9]{8}',dni): return fail('El DNI debe tener 8 dígitos.')
    phone=textval(data,'phone',6,25)
    if not re.fullmatch(r'[+\d ()-]{6,25}',phone): return fail('Revisa el teléfono de contacto.')
    room=next((r for r in CONFIG['rooms'] if data.get('room_id') in (r['id'],public_room(r)['id'])),None)
    if not room or not room.get('active',True) or room['capacity']<guests: return fail('Habitación no válida para el número de huéspedes.')
    if limited('book:'+str(session['uid']),10,3600): return fail('Has enviado varias reservas. Contacta con recepción.',429)
    request_key=data.get('request_key')
    if request_key is not None and (not isinstance(request_key,str) or not re.fullmatch(r'[A-Za-z0-9-]{16,80}',request_key)): return fail('Código de solicitud inválido.')
    con=db(); lock_room(con,room['id'])
    if request_key:
        previous=con.execute('SELECT id,total,status FROM bookings WHERE user_id=? AND request_key=?',(session['uid'],request_key)).fetchone()
        if previous: con.rollback(); return jsonify(dict(previous)),200
    units=free_units(room,a,b)
    if not units: con.rollback(); return fail('Esta habitación acaba de agotarse. Busca otra fecha.',409)
    booking_id='RN-'+secrets.token_hex(4).upper()
    con.execute('INSERT INTO bookings(id,user_id,room_id,unit,arrival,departure,guests,total,phone,request_key) VALUES(?,?,?,?,?,?,?,?,?,?)',(booking_id,session['uid'],room['id'],units[0],a,b,guests,room['price']*nights,phone,request_key));con.execute('UPDATE bookings SET dni=? WHERE id=?',(dni,booking_id));enqueue(con,booking_id,'solicitud recibida');con.commit()
    return jsonify(id=booking_id,total=room['price']*nights,status='pendiente'),201
@app.route('/api/reviews',methods=['GET','POST'])
def reviews():
    if request.method=='GET': return jsonify(reviews=[dict(r) for r in db().execute('SELECT r.id,u.name,r.rating,r.body,r.created FROM reviews r JOIN users u ON u.id=r.user_id WHERE approved=1 ORDER BY r.created DESC LIMIT 50')])
    if not session.get('uid'): return fail('Inicia sesión para escribir una reseña.',401)
    data=request.get_json(); body=textval(data,'body',15,1000)
    try: rating=int(data.get('rating',0))
    except (TypeError,ValueError): return fail('Selecciona una valoración.')
    if rating not in range(1,6): return fail('Selecciona una valoración de 1 a 5.')
    try: db().execute('INSERT INTO reviews(user_id,rating,body) VALUES(?,?,?)',(session['uid'],rating,body)); db().commit()
    except sqlite3.IntegrityError: return fail('Ya enviaste una reseña. Gracias por compartir tu experiencia.',409)
    return jsonify(message='Gracias. Tu reseña se publicará después de su revisión.'),201
@app.post('/api/contact')
def contact():
    if limited('contact',5,3600): return fail('Espera antes de enviar otro mensaje.',429)
    data=request.get_json(); name=textval(data,'name',2,80);email=emailval(data); body=textval(data,'body',10,2000)
    if data.get('consent') is not True: return fail('Acepta el uso de tus datos para responder tu consulta.')
    db().execute('INSERT INTO messages(name,email,body) VALUES(?,?,?)',(name,email,body));db().commit()
    return jsonify(message='Tu consulta fue registrada. Recepción podrá revisarla en su panel.'),201
@app.get('/api/admin')
@admin_required
def admin():
    return jsonify(bookings=[dict(r) for r in db().execute('SELECT b.*,u.name,u.email FROM bookings b JOIN users u ON b.user_id=u.id ORDER BY b.created DESC LIMIT 500')],reviews=[dict(r) for r in db().execute('SELECT r.*,u.name FROM reviews r JOIN users u ON r.user_id=u.id ORDER BY r.id DESC LIMIT 500')],messages=[dict(r) for r in db().execute('SELECT * FROM messages ORDER BY id DESC LIMIT 500')])
@app.post('/api/admin/notifications/read')
@admin_required
def admin_notifications_read():
    rows=db().execute("SELECT id,payload FROM notification_outbox WHERE status='pendiente'").fetchall()
    ids=[]
    for row in rows:
        try: event=json.loads(row['payload']).get('event','')
        except (TypeError,ValueError): event=''
        if event in ('solicitud recibida','reserva solicitada con pago al llegar'): ids.append(row['id'])
    if ids:
        placeholders=','.join('?' for _ in ids)
        db().execute(f"UPDATE notification_outbox SET status='leida' WHERE id IN ({placeholders})",tuple(ids));db().commit()
    return jsonify(ok=True,read=len(ids))

@app.post('/api/admin/bookings/<booking_id>')
@admin_required
def admin_booking(booking_id):
    status=request.get_json().get('status'); row=db().execute('SELECT * FROM bookings WHERE id=?',(booking_id,)).fetchone()
    if not row: return fail('Reserva no encontrada.',404)
    allowed={'pendiente':['confirmada','libre'],'confirmada':['completada','libre'],'libre':[],'completada':[]}
    if status not in allowed.get(row['status'],[]): return fail('Cambio de estado no permitido.',409)
    if status=='confirmada':
        if row['payment_status']!='aprobado' and row['payment_method']!='arrival': return fail('Verifica el pago o la modalidad de pago al llegar.',409)
        if request.get_json().get('identity_verified') is not True: return fail('Confirma que verificaste el documento y la mayoría de edad.',409)
    if status=='completada' and row['departure']>today().isoformat(): return fail('La estancia aún no ha terminado.')
    snapshot=None
    if status=='confirmada':
        room=next(r for r in CONFIG['rooms'] if r['id']==row['room_id'])
        snapshot=json.dumps({k:room.get(k,'Por confirmar con recepción') for k in ['number','name','floor','side','window','directions','beds','features']},ensure_ascii=False)
    cur=db().execute("UPDATE bookings SET status=?,room_report=COALESCE(?,room_report),identity_checked=CASE WHEN ?='confirmada' THEN 1 ELSE identity_checked END WHERE id=? AND status=? AND (arrival_deadline IS NULL OR arrival_deadline>? OR payment_status='aprobado')",(status,snapshot,status,booking_id,row['status'],time.time())); db().commit()
    if not cur.rowcount:return fail('La reserva cambió. Actualiza el panel.',409)
    return jsonify(ok=True)
@app.post('/api/admin/reviews/<int:review_id>')
@admin_required
def moderate(review_id):
    approved=request.get_json().get('approved')
    if not isinstance(approved,bool): return fail('Estado no válido.')
    db().execute('UPDATE reviews SET approved=? WHERE id=?',(int(approved),review_id));db().commit();return jsonify(ok=True)
DUMMY_HASH=generate_password_hash(secrets.token_hex(24))
if not POSTGRES: init()
if os.environ.get('TRUST_PROXY')=='1':
    from werkzeug.middleware.proxy_fix import ProxyFix
    app.wsgi_app=ProxyFix(app.wsgi_app,x_for=1,x_proto=1)

@app.get('/healthz')
def health():
    db().execute('SELECT 1').fetchone()
    return jsonify(status='ok')

@app.errorhandler(BusyDatabase)
@app.errorhandler(sqlite3.OperationalError)
def overloaded(error):
    response=jsonify(error='Hay alta demanda. Espera unos segundos y vuelve a intentarlo.'); response.status_code=503; response.headers['Retry-After']='3'; return response

import time
from ecosystem_v6 import install_ecosystem, customer_bookings, start_expiry_worker
from extensions import install
install(app, globals())
from payments_v5 import install_payments
install_payments(app,globals())
install_ecosystem(app,globals())

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1] in ('create-admin','reset-password'):
        email=input('Correo: ').strip().lower(); password=getpass.getpass('Contraseña nueva (mínimo 10 caracteres): ')
        if len(password)<10 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email): sys.exit('Datos inválidos.')
        with app.app_context():
            if sys.argv[1]=='create-admin':
                name=input('Nombre: ').strip() or 'Recepción'
                try: db().execute('INSERT INTO users(name,email,password,admin) VALUES(?,?,?,1)',(name,email,generate_password_hash(password)))
                except sqlite3.IntegrityError: sys.exit('El correo ya existe. No se modificaron sus permisos.')
            else:
                cur=db().execute('UPDATE users SET password=?,session_version=session_version+1 WHERE email=?',(generate_password_hash(password),email))
                if not cur.rowcount: sys.exit('No existe ese correo.')
            db().commit()
        print('Operación completada.')
    else:
        from waitress import serve
        start_expiry_worker(app,db)
        print('Abre http://127.0.0.1:5000 — Ctrl+C para detener')
        serve(app,host=os.environ.get('HOST','127.0.0.1'),port=int(os.environ.get('PORT','5000')))
