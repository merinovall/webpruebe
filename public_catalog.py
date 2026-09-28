import re,hashlib

def public_room(room):
    keys=['price','capacity','size','beds','image','features','category','example','active']
    out={k:room[k] for k in keys if k in room}
    out['id']=room.get('public_id') or hashlib.sha256(room['id'].encode()).hexdigest()[:24]
    out['name']=re.sub(r'^\s*\d{1,3}\s*[·:—-]\s*','',room['name'])
    out['description']=re.sub(r'Ubicada en el piso[^.]*\.?','',room.get('description',''),flags=re.I).strip()
    return out

def public_hotel(config):
    return {**config,'rooms':[public_room(r) for r in config['rooms'] if r.get('active',True)]}
