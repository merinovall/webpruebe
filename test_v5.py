import os,tempfile,unittest,io
os.environ['HOTEL_DATA_DIR']=tempfile.mkdtemp(prefix='hotel-v5-')
from app import app,db,today,CONFIG
from werkzeug.security import generate_password_hash
from datetime import timedelta
from PIL import Image
class BookingPayments(unittest.TestCase):
 def test_flow(self):
  c=app.test_client();a=app.test_client();other=app.test_client()
  def post(client,path,d,t):return client.post('/api/'+path,json=d,headers={'X-CSRF-Token':t})
  def register(client,email):
   t=client.get('/api/bootstrap').json['csrf'];return post(client,'register',dict(name='Cliente de prueba',email=email,password='Prueba-Segura-123',consent=True),t).json['csrf']
  t=register(c,'cliente@example.test');ot=register(other,'otro@example.test')
  with app.app_context():
   db().execute('INSERT INTO users(name,email,password,admin) VALUES(?,?,?,1)',('Admin','admin@example.test',generate_password_hash('Admin-Seguro-123')));db().commit()
  at=a.get('/api/bootstrap').json['csrf'];at=post(a,'login',dict(email='admin@example.test',password='Admin-Seguro-123'),at).json['csrf']
  self.assertEqual(c.get('/admin').status_code,302);self.assertEqual(a.get('/admin').status_code,200)
  self.assertEqual(len(CONFIG['rooms']),23);self.assertEqual([r['number'] for r in CONFIG['rooms']],[f'{i:03}' for i in range(1,24)])
  d=dict(room_id='simple',arrival=(today()+timedelta(days=2)).isoformat(),departure=(today()+timedelta(days=3)).isoformat(),guests=1,phone='999888777',dni='12345678',birthdate='2000-01-01')
  r=post(c,'bookings',d,t);self.assertEqual(r.status_code,201,r.json);bid=r.json['id']
  self.assertEqual(post(a,'admin/bookings/'+bid,{'status':'confirmada','identity_verified':True},at).status_code,409)
  self.assertEqual(post(c,'bookings/'+bid+'/pay-arrival',{},t).status_code,200)
  self.assertEqual(post(c,'bookings/'+bid+'/pay-arrival',{},t).status_code,200)
  self.assertEqual(a.get('/api/admin/metrics').json['income']['Hoy'],0)
  self.assertEqual(post(a,'admin/bookings/'+bid,{'status':'confirmada'},at).status_code,409)
  self.assertEqual(post(a,'admin/bookings/'+bid,{'status':'confirmada','identity_verified':True},at).status_code,200)
  self.assertEqual(post(a,'admin/payments/'+bid,{'verified':True},at).status_code,200)
  self.assertEqual(a.get('/api/admin/metrics').json['income']['Hoy'],70)
  r=post(c,'bookings',{**d,'room_id':'doble'},t);bid2=r.json['id']
  def image():
   f=io.BytesIO();Image.new('RGB',(100,100),'white').save(f,format='PNG');f.seek(0);return f
  path='/api/bookings/'+bid2+'/receipt'
  self.assertEqual(other.post(path,data={'reference':'TEST-123','receipt':(image(),'test.png')},headers={'X-CSRF-Token':ot}).status_code,404)
  self.assertEqual(c.post(path,data={'reference':'TEST-123','receipt':(io.BytesIO(b'bad'),'bad.png')},headers={'X-CSRF-Token':t}).status_code,400)
  self.assertEqual(c.post(path,data={'reference':'TEST-123','receipt':(image(),'test.png')},headers={'X-CSRF-Token':t}).status_code,200)
  self.assertEqual(c.get(path).status_code,200);self.assertEqual(a.get(path).status_code,200);self.assertEqual(other.get(path).status_code,404);self.assertEqual(app.test_client().get(path).status_code,401)
  self.assertEqual(post(c,'bookings/'+bid2+'/pay-arrival',{},t).status_code,409)
  self.assertEqual(post(a,'admin/payments/'+bid2,{'verified':True},at).status_code,200)
  self.assertEqual(post(a,'admin/bookings/'+bid2,{'status':'confirmada','identity_verified':True},at).status_code,200)
  self.assertEqual(a.get('/api/admin/metrics').json['income']['Hoy'],170)
  self.assertEqual(a.get('/api/admin/overview').status_code,200)
  with app.app_context():
   rows=db().execute('SELECT payload FROM notification_outbox').fetchall();self.assertTrue(any('12345678' in row['payload'] for row in rows))
if __name__=='__main__':unittest.main()
