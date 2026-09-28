import os,tempfile,unittest,io
os.environ['HOTEL_DATA_DIR']=tempfile.mkdtemp(prefix='hotel-test-')
from app import app,db,today,CONFIG
from datetime import timedelta
from werkzeug.security import generate_password_hash
class Flow(unittest.TestCase):
 def test_reservation_payment_security(self):
  c=app.test_client();token=c.get('/api/bootstrap').json['csrf']
  def post(client,path,data,csrf):return client.post('/api/'+path,json=data,headers={'X-CSRF-Token':csrf})
  self.assertEqual(c.post('/api/register',json={}).status_code,403)
  r=post(c,'register',dict(name='Cliente Prueba',email='cliente@example.test',password='Test-password-123',consent=True),token);self.assertEqual(r.status_code,200);token=r.json['csrf']
  self.assertEqual(c.get('/api/admin').status_code,403)
  data=dict(room_id='simple',arrival=(today()+timedelta(days=2)).isoformat(),departure=(today()+timedelta(days=3)).isoformat(),guests=1,phone='999888777',dni='12345678',birthdate='2000-01-01',request_key='retry-reservation-12345')
  self.assertEqual(post(c,'bookings',{**data,'birthdate':today().isoformat()},token).status_code,400)
  r=post(c,'bookings',data,token);self.assertEqual(r.status_code,201,r.json);bid=r.json['id']
  self.assertEqual(post(c,'bookings',data,token).json['id'],bid)
  with app.app_context():
   db().execute('INSERT INTO users(name,email,password,admin) VALUES(?,?,?,1)',('Admin','admin@example.test',generate_password_hash('Admin-password-123')));db().commit()
  ad=app.test_client();at=ad.get('/api/bootstrap').json['csrf'];at=post(ad,'login',dict(email='admin@example.test',password='Admin-password-123'),at).json['csrf']
  self.assertEqual(post(ad,'admin/bookings/'+bid,{'status':'confirmada'},at).status_code,409)
  self.assertEqual(post(c,'bookings/'+bid+'/payment',dict(method='yape',reference='OPERACION-TEST'),token).status_code,200)
  self.assertEqual(post(c,'admin/payments/'+bid,{'verified':True},token).status_code,403)
  self.assertEqual(post(ad,'admin/payments/'+bid,{'verified':True},at).status_code,200)
  self.assertEqual(post(ad,'admin/payments/'+bid,{'verified':True},at).status_code,409)
  self.assertEqual(post(ad,'admin/bookings/'+bid,{'status':'confirmada'},at).status_code,200)
  self.assertEqual(ad.get('/api/admin/metrics').json['income']['Hoy'],70)
  other=app.test_client();ot=other.get('/api/bootstrap').json['csrf'];ot=post(other,'register',dict(name='Otro Usuario',email='otro@example.test',password='Another-password-123',consent=True),ot).json['csrf']
  self.assertEqual(post(other,'bookings/'+bid+'/payment',dict(method='yape',reference='OTRA-TEST'),ot).status_code,409)
  self.assertEqual(ad.post('/api/admin/photo',data={'target':'logo','photo':(io.BytesIO(b'<script>bad</script>'),'bad.png')},headers={'X-CSRF-Token':at}).status_code,400)
  from PIL import Image
  from pathlib import Path
  root=Path(__file__).resolve().parent; original=(root/'hotel.json').read_bytes(); saved=None
  try:
   photo=io.BytesIO();Image.new('RGB',(32,32),'white').save(photo,format='PNG');photo.seek(0)
   upload=ad.post('/api/admin/photo',data={'target':'logo','photo':(photo,'real.png')},headers={'X-CSRF-Token':at});self.assertEqual(upload.status_code,200,upload.json)
   saved=CONFIG['logo'];self.assertTrue((root/'static/img'/saved).exists())
  finally:
   (root/'hotel.json').write_bytes(original)
   if saved:(root/'static/img'/saved).unlink(missing_ok=True)
  self.assertEqual(c.post('/api/admin/photo',data={'target':'logo','photo':(io.BytesIO(b'bad'),'bad.png')},headers={'X-CSRF-Token':token}).status_code,403)
  self.assertEqual(post(c,'email',dict(email='nuevo@example.test',current='Test-password-123'),token).status_code,200)
  self.assertEqual(post(c,'password',dict(current='Test-password-123',password='Updated-password-123'),token).status_code,200)
  self.assertEqual(c.get('/api/bookings').status_code,401)
if __name__=='__main__':unittest.main()
