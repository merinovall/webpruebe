import os,tempfile,unittest,time,json,shutil
from pathlib import Path
TMP=Path(tempfile.mkdtemp(prefix='hotel-v6-'))
os.environ['HOTEL_DATA_DIR']=str(TMP/'data')
shutil.copyfile(Path(__file__).with_name('hotel.json'),TMP/'hotel.json')
os.environ['HOTEL_CONFIG_FILE']=str(TMP/'hotel.json')
from app import app,db,today,CONFIG
from datetime import timedelta
from ecosystem_v6 import expire
class Ecosystem(unittest.TestCase):
 def test_full_flow(self):
  c=app.test_client();a=app.test_client();other=app.test_client()
  def register(client,email):
   token=client.get('/api/bootstrap').json['csrf']
   r=client.post('/api/register',json=dict(name='Cliente Prueba',email=email,password='Prueba-segura-123',consent=True),headers={'X-CSRF-Token':token});self.assertEqual(r.status_code,200,r.json);return r.json['csrf']
  t=register(c,'customer@example.test');at=register(a,'admin@example.test');ot=register(other,'other@example.test')
  with app.app_context():db().execute("UPDATE users SET admin=1 WHERE email='admin@example.test'");db().commit()
  def post(client,path,payload,token):return client.post('/api/'+path,json=payload,headers={'X-CSRF-Token':token})
  d=dict(room_id='simple',arrival=today().isoformat(),departure=(today()+timedelta(days=2)).isoformat(),guests=1,phone='999888777',dni='12345678')
  r=post(c,'bookings',d,t);self.assertEqual(r.status_code,201,r.json);bid=r.json['id']
  self.assertEqual(post(c,'bookings/'+bid+'/pay-arrival',{},t).status_code,200)
  b=c.get('/api/bookings').json['bookings'][0];deadline=b['arrival_deadline'];self.assertTrue(3590<deadline-time.time()<=3600)
  self.assertNotIn('birthdate',b);self.assertNotIn('identity_checked',b);self.assertIsNone(b['report'])
  post(c,'bookings/'+bid+'/pay-arrival',{},t);self.assertEqual(c.get('/api/bookings').json['bookings'][0]['arrival_deadline'],deadline)
  self.assertEqual(post(a,'admin/bookings/'+bid,{'status':'confirmada'},at).status_code,409)
  self.assertEqual(post(a,'admin/bookings/'+bid,{'status':'confirmada','identity_verified':True},at).status_code,200)
  with app.app_context():expire(db(),deadline+1)
  self.assertEqual(c.get('/api/bookings').json['bookings'],[])
  self.assertEqual(post(a,'admin/payments/'+bid,{'verified':True},at).status_code,409)
  self.assertEqual(a.get('/api/admin').json['bookings'][0]['status'],'cancelada')
  self.assertEqual(a.get('/api/admin/metrics').json['income']['Hoy'],0)
  # Released inventory, with no renewal of the old request's clock.
  r=post(c,'bookings',d,t);self.assertEqual(r.status_code,201,r.json);bid=r.json['id']
  post(c,'bookings/'+bid+'/pay-arrival',{},t)
  self.assertEqual(post(a,'admin/payments/'+bid,{'verified':True},at).status_code,200)
  self.assertEqual(c.get('/api/bookings/'+bid+'/report').status_code,404)
  self.assertEqual(post(a,'admin/bookings/'+bid,{'status':'confirmada','identity_verified':True},at).status_code,200)
  b=c.get('/api/bookings').json['bookings'][0];self.assertEqual(b['report']['number'],'001')
  with app.app_context():expire(db(),b['arrival_deadline']+1)
  self.assertEqual(c.get('/api/bookings').json['bookings'][0]['status'],'confirmada')
  self.assertEqual(other.get('/api/bookings/'+bid+'/report').status_code,404)
  response=c.get('/api/bookings/'+bid+'/report');self.assertEqual(response.status_code,200);self.assertIn('Piso:',response.text);response.close()
  # Protected room edits; price changes do not alter accepted reservations.
  room=dict(CONFIG['rooms'][0]);room.update(price=999,floor='5',side='Ala este',window='Sin ventana',directions='Usa el ascensor principal.',active=False)
  self.assertEqual(post(c,'admin/rooms/simple',room,t).status_code,403)
  self.assertEqual(a.post('/api/admin/rooms/simple',json=room).status_code,403)
  self.assertEqual(post(a,'admin/rooms/simple',{**room,'price':-1},at).status_code,400)
  self.assertEqual(post(a,'admin/rooms/simple',{**room,'number':'002'},at).status_code,400)
  self.assertEqual(post(a,'admin/rooms/simple',room,at).status_code,200)
  b=c.get('/api/bookings').json['bookings'][0];self.assertEqual(b['total'],d['departure']!=d['arrival'] and 140);self.assertEqual(b['report']['floor'],'1')
  self.assertEqual(post(c,'bookings',{**d,'arrival':(today()+timedelta(days=3)).isoformat(),'departure':(today()+timedelta(days=4)).isoformat()},t).status_code,400)
  with app.app_context():db().execute("UPDATE bookings SET departure=?,status='completada' WHERE id=?",(today().isoformat(),bid));db().commit()
  self.assertEqual(c.get('/api/bookings').json['bookings'],[]);self.assertEqual(c.get('/api/bookings/'+bid+'/report').status_code,404)
  self.assertEqual(len(a.get('/api/admin').json['bookings']),2)
if __name__=='__main__':unittest.main()
