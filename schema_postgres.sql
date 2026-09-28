-- Ejecutar una vez ANTES de arrancar los procesos web.
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE TABLE IF NOT EXISTS users(id BIGSERIAL PRIMARY KEY,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password TEXT NOT NULL,admin INTEGER DEFAULT 0,session_version INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS bookings(id TEXT PRIMARY KEY,user_id BIGINT REFERENCES users(id),room_id TEXT NOT NULL,unit INTEGER NOT NULL,arrival TEXT NOT NULL,departure TEXT NOT NULL,guests INTEGER,total INTEGER,status TEXT DEFAULT 'pendiente',phone TEXT,created TEXT DEFAULT (CURRENT_TIMESTAMP::text),request_key TEXT);
CREATE UNIQUE INDEX IF NOT EXISTS booking_retry ON bookings(user_id,request_key);
CREATE INDEX IF NOT EXISTS booking_user ON bookings(user_id,created DESC);
CREATE INDEX IF NOT EXISTS booking_dates ON bookings(room_id,arrival,departure,status);
-- Las fechas ISO se convierten mediante make_date (inmutable) para la restricción.
DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname='no_overlapping_stays') THEN
  ALTER TABLE bookings ADD CONSTRAINT no_overlapping_stays EXCLUDE USING gist
  (room_id WITH =,unit WITH =,daterange(make_date(substring(arrival,1,4)::int,substring(arrival,6,2)::int,substring(arrival,9,2)::int),make_date(substring(departure,1,4)::int,substring(departure,6,2)::int,substring(departure,9,2)::int),'[)') WITH &&)
  WHERE (status IN ('pendiente','confirmada'));
 END IF;
END $$;
CREATE TABLE IF NOT EXISTS reviews(id BIGSERIAL PRIMARY KEY,user_id BIGINT UNIQUE REFERENCES users(id),rating INTEGER CHECK(rating BETWEEN 1 AND 5),body TEXT,approved INTEGER DEFAULT 0,created TEXT DEFAULT (CURRENT_TIMESTAMP::text));
CREATE TABLE IF NOT EXISTS messages(id BIGSERIAL PRIMARY KEY,name TEXT,email TEXT,body TEXT,created TEXT DEFAULT (CURRENT_TIMESTAMP::text));
CREATE TABLE IF NOT EXISTS attempts(key TEXT PRIMARY KEY,count INTEGER,expires DOUBLE PRECISION);

ALTER TABLE users ADD COLUMN IF NOT EXISTS must_change INTEGER DEFAULT 0;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS dni TEXT;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS birthdate TEXT;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS payment_status TEXT DEFAULT 'sin informar';
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS payment_method TEXT;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS payment_reference TEXT;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS paid_at TEXT;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS verified_by INTEGER;
CREATE TABLE IF NOT EXISTS notification_outbox(id TEXT PRIMARY KEY,payload TEXT NOT NULL,status TEXT NOT NULL);
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS receipt_file TEXT;

ALTER TABLE bookings ADD COLUMN IF NOT EXISTS arrival_deadline DOUBLE PRECISION;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS identity_checked INTEGER DEFAULT 0;
ALTER TABLE bookings ADD COLUMN IF NOT EXISTS room_report TEXT;
CREATE INDEX IF NOT EXISTS expiry_deadlines ON bookings(arrival_deadline,status);
