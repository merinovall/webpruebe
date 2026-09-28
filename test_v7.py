import os,tempfile,unittest,io
os.environ['HOTEL_DATA_DIR']=tempfile.mkdtemp(prefix='hotel-v7-')
from app import app,db,today,CONFIG
from datetime import timedelta
from PIL import Image
class Changes(unittest.TestCase):
 def test_privacy_booking_and_reviews(self):
  c=app.test_client();other=app.test_client();public=c.get('/api/bootstrap').json
  room=public['hotel']['rooms'][0];self.assertNotIn('number',room);self.assertNotIn('floor',room);self.assertNotIn('001',room['name']);self.assertNotIn('habitacion-',room['id'])
  def reg(client,email):
   token=client.get('/api/bootstrap').json['csrf'];return client.post('/api/register',json=dict(name='Cliente Prueba',email=email,password='Prueba-segura-123',consent=True),headers={'X-CSRF-Token':token}).json['csrf']
  t=reg(c,'v7@example.test');o=reg(other,'v7other@example.test')
  def post(path,data):return c.post('/api/'+path,json=data,headers={'X-CSRF-Token':t})
  self.assertEqual(post('reviews',{'body':'Una buena atención desde la primera consulta.','rating':5}).status_code,201)
  self.assertEqual(c.get('/api/reviews').json['reviews'],[])
  a=today().isoformat();b=(today()+timedelta(days=1)).isoformat();q={'arrival':a,'departure':b,'guests':1}
  bid=post('bookings',{**q,'room_id':room['id'],'phone':'999888777','dni':'12345678'}).json['id']
  own=c.get('/api/bookings').json['bookings'][0];self.assertEqual(own['assigned_number'],'001');self.assertEqual(other.get('/api/bookings').json['bookings'],[])
  result=other.get('/api/availability',query_string=q).json['rooms'];self.assertEqual(next(x for x in result if x['id']==room['id'])['available'],0);self.assertTrue(all('number' not in x for x in result))
  self.assertEqual(post('bookings',{**q,'room_id':room['id'],'phone':'999888777','dni':'12345678'}).status_code,409)
  f=io.BytesIO();Image.new('RGB',(20,20)).save(f,'PNG');f.seek(0)
  receipt=c.post('/api/bookings/'+bid+'/receipt',data={'receipt':(f,'proof.png')},headers={'X-CSRF-Token':t});self.assertEqual(receipt.status_code,200,receipt.json)
  with app.app_context():
   db().execute("UPDATE bookings SET status='cancelada' WHERE id=?",(bid,));db().commit()
  result=other.get('/api/availability',query_string=q).json['rooms'];self.assertEqual(next(x for x in result if x['id']==room['id'])['available'],1)
  self.assertNotIn('Escenario conceptual generado',c.get('/').text);self.assertNotIn('id="videoToggle"',c.get('/').text)
if __name__=='__main__':unittest.main()
