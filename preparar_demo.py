"""Inicialización explícita local. Nunca ejecutar en un servidor publicado."""
import os
if os.environ.get('HOTEL_HTTPS')=='1' or os.environ.get('DATABASE_URL'):
    raise SystemExit('Este comando está reservado a la demostración local.')
from app import app,db
from werkzeug.security import generate_password_hash
with app.app_context():
    if db().execute('SELECT id FROM users WHERE email=?',('pruebaht@gmail.com',)).fetchone():
        print('La cuenta ya existe; no se cambió su contraseña ni sus permisos.')
    else:
        db().execute('INSERT INTO users(name,email,password,admin,must_change) VALUES(?,?,?,1,1)',('Administrador','pruebaht@gmail.com',generate_password_hash('132007')))
        db().commit()
        print('Cuenta local creada. Al iniciar sesión debes cambiar la contraseña inicial.')
