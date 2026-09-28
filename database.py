"""SQLite para desarrollo; PostgreSQL con pool por proceso en producción."""
import os, sqlite3, threading, atexit
from pathlib import Path
URL=os.environ.get('DATABASE_URL','')
POSTGRES=bool(URL)
_pool=None
_lock=threading.Lock()
class BusyDatabase(Exception): pass
class Record(dict):
    def __getitem__(self,key):
        return tuple(self.values())[key] if isinstance(key,int) else super().__getitem__(key)
def row_factory(cursor):
    names=[col.name for col in cursor.description] if cursor.description else []
    return lambda values: Record(zip(names,values))
def pool():
    global _pool
    if _pool is None:
        with _lock:
            if _pool is None:
                from psycopg_pool import ConnectionPool
                _pool=ConnectionPool(URL,min_size=1,max_size=int(os.environ.get('DB_POOL_SIZE','8')),timeout=3,max_waiting=32,
                    kwargs={'row_factory':row_factory,'options':'-c statement_timeout=5000 -c lock_timeout=3000'},open=True)
                atexit.register(_pool.close)
    return _pool
class Result:
    def __init__(self,cursor,lastrowid=None):self.cursor=cursor;self.lastrowid=lastrowid
    @property
    def rowcount(self):return self.cursor.rowcount
    def fetchone(self):return self.cursor.fetchone()
    def fetchall(self):return self.cursor.fetchall()
    def __iter__(self):return iter(self.cursor)
class PgConnection:
    def __init__(self):
        from psycopg_pool import PoolTimeout,TooManyRequests
        try:self.raw=pool().getconn()
        except (PoolTimeout,TooManyRequests) as e:raise BusyDatabase() from e
    def execute(self,sql,params=()):
        import psycopg
        sql=sql.replace('?','%s')
        user_insert=sql.lstrip().upper().startswith('INSERT INTO USERS(')
        if user_insert:sql+=' RETURNING id'
        try:
            cur=self.raw.execute(sql,params)
            inserted=cur.fetchone()['id'] if user_insert else None
            return Result(cur,inserted)
        except psycopg.IntegrityError as e:raise sqlite3.IntegrityError(str(e)) from e
        except (psycopg.errors.LockNotAvailable,psycopg.errors.QueryCanceled,psycopg.OperationalError) as e:raise BusyDatabase() from e
    def commit(self):self.raw.commit()
    def rollback(self):self.raw.rollback()
    def close(self):
        try:self.raw.rollback()
        finally:pool().putconn(self.raw)
def connect(data):
    if POSTGRES:return PgConnection()
    conn=sqlite3.connect(Path(data)/'hotel.sqlite3',timeout=3)
    conn.row_factory=sqlite3.Row
    conn.execute('PRAGMA foreign_keys=ON')
    return conn

def lock_room(conn,room_id):
    if POSTGRES:conn.execute('SELECT pg_advisory_xact_lock(hashtext(?))',(room_id,))
    else:conn.execute('BEGIN IMMEDIATE')

def init_postgres():
    import psycopg
    schema=Path(__file__).with_name('schema_postgres.sql').read_text()
    with psycopg.connect(URL) as conn:conn.execute(schema)
