"""Regenera index.html para Live Server después de editar hotel.json."""
from pathlib import Path
import json
from public_catalog import public_hotel
from datetime import date
from jinja2 import Environment,FileSystemLoader,select_autoescape
root=Path(__file__).resolve().parent
hotel=public_hotel(json.loads((root/'hotel.json').read_text(encoding='utf8')))
env=Environment(loader=FileSystemLoader(root/'templates'),autoescape=select_autoescape(['html']))
html=env.get_template('index.html').render(hotel=hotel)
html=html.replace('<script src="/static/app.js" defer></script>','<script src="static/preview-data.js"></script><script src="static/app.js" defer></script>')
html=html.replace('src="/static/','src="static/').replace('href="/static/','href="static/')
(root/'index.html').write_text(html,encoding='utf8')
(root/'static/preview-data.js').write_text('window.HOTEL_PREVIEW='+json.dumps({'hotel':hotel,'user':None,'csrf':'','today':date.today().isoformat(),'google_enabled':False},ensure_ascii=False)+';',encoding='utf8')
print('index.html actualizado. Abre la carpeta del proyecto como raíz de Live Server.')
