"""Cola transaccional de avisos. No envía nada sin configuración explícita."""
import json,secrets

def enqueue(con,bid,event):
    row=con.execute('SELECT b.id,b.total,b.arrival,b.departure,b.room_id,b.dni,u.name FROM bookings b JOIN users u ON u.id=b.user_id WHERE b.id=?',(bid,)).fetchone()
    if row:
        payload={**dict(row),'event':event}
        con.execute('INSERT INTO notification_outbox(id,payload,status) VALUES(?,?,?)',(secrets.token_hex(12),json.dumps(payload,ensure_ascii=False),'pendiente'))
