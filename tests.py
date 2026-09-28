"""Pruebas de integración aisladas. No alteran la base de datos del hotel."""
import os,tempfile,unittest
from datetime import timedelta
os.environ.pop('DATABASE_URL',None)
_tmp=tempfile.TemporaryDirectory()
os.environ['HOTEL_DATA_DIR']=_tmp.name
from app import app,db,today
class HotelTests(unittest.TestCase):
 def setUp(self):
  self.c=app.test_client();self.csrf=self.c.get('/api/bootstrap').json['csrf']
 def post(self,path,data,client=None,token=None):
  return (client or self.c).post('/api/'+path,json=data,headers={'X-CSRF-Token':token or self.csrf})
 def register(self,email):
  r=self.post('register',dict(name='Usuario de prueba',email=email,password='Prueba-segura-123',consent=True));self.assertEqual(r.status_code,200);self.csrf=r.json['csrf']
 def test_complete_flow(self):
  self.assertEqual(self.c.post('/api/login',json={}).status_code,403)
  self.assertEqual(self.c.get('/api/admin').status_code,401)
  self.register('cliente@example.com')
  self.assertEqual(self.c.get('/api/admin').status_code,403)
  d=dict(room_id='simple',arrival=(today()+timedelta(days=3)).isoformat(),departure=(today()+timedelta(days=5)).isoformat(),guests=1,phone='+51 999999999',total=1)
  first=self.post('bookings',d);self.assertEqual(first.status_code,201);self.assertEqual(first.json['total'],140)
  second=self.post('bookings',d);self.assertEqual(second.status_code,201)
  third=self.post('bookings',d);self.assertEqual(third.status_code,409)
  self.assertEqual(self.post('bookings',{**d,'guests':4}).status_code,400)
  self.assertEqual(self.post('bookings',{**d,'arrival':d['departure']}).status_code,400)
  other=app.test_client();tok=other.get('/api/bootstrap').json['csrf'];reg=self.post('register',dict(name='Otro usuario',email='otro@example.com',password='Prueba-segura-456',consent=True),other,tok);tok=reg.json['csrf']
  self.assertEqual(len(other.get('/api/bookings').json['bookings']),0)
  self.assertEqual(self.post('bookings/'+first.json['id']+'/cancel',{},other,tok).status_code,409)
  self.assertEqual(self.post('bookings/'+first.json['id']+'/cancel',{}).status_code,200)
  self.assertEqual(self.post('bookings',d).status_code,201)
  self.assertEqual(self.post('reviews',dict(rating=5,body='Buena estancia en este lugar.')).status_code,400)
  self.assertEqual(self.post('contact',dict(name='Consulta',email='consulta@example.com',body='Necesito información de habitaciones.',consent=True)).status_code,201)
  with app.app_context():
   db().execute("UPDATE users SET admin=1 WHERE email='otro@example.com'")
   db().execute("UPDATE bookings SET status='completada',arrival=?,departure=? WHERE id=?",((today()-timedelta(days=2)).isoformat(),today().isoformat(),second.json['id']));db().commit()
  self.assertEqual(self.post('reviews',dict(rating=5,body='Una estancia cómoda, gracias.')).status_code,201)
  self.assertEqual(len(self.c.get('/api/reviews').json['reviews']),0)
  adm=other.get('/api/admin');self.assertEqual(adm.status_code,200);rid=adm.json['reviews'][0]['id']
  self.assertEqual(self.post('admin/reviews/'+str(rid),dict(approved=True),other,tok).status_code,200)
  self.assertEqual(len(self.c.get('/api/reviews').json['reviews']),1)
  self.assertEqual(self.post('password',dict(current='Prueba-segura-123',password='Nueva-clave-123')).status_code,200)
  self.assertEqual(self.c.get('/api/bookings').status_code,401)
  self.csrf=self.c.get('/api/bootstrap').json['csrf']
  self.assertEqual(self.post('login',dict(email='cliente@example.com',password='Nueva-clave-123')).status_code,200)
  self.assertIn("default-src 'self'",self.c.get('/').headers['Content-Security-Policy'])
if __name__=='__main__':unittest.main()
