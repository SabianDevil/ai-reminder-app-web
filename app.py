import os
from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime, timedelta
import re
# Hapus import pytz dan kode terkait timezone untuk sementara saat testing SQLite,
# atau pastikan scheduled_time disimpan sebagai naive datetime
# Jika ingin tetap menyimpan sebagai aware datetime, tambahkan default tzinfo untuk SQLite.

# --- INISIALISASI APLIKASI FLASK ---
app = Flask(__name__)

# --- KONFIGURASI DATABASE ---
# Perubahan di sini untuk menggunakan SQLite
# DATABASE_URL = os.getenv("DATABASE_URL") # Hapus atau komen baris ini
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db") # Gunakan SQLite lokal jika DATABASE_URL tidak diset

# --- DEBUGGING PENTING DI SINI ---
print(f"DEBUG: DATABASE_URL yang diterima: '{DATABASE_URL}'") 
if not DATABASE_URL:
    print("ERROR: DATABASE_URL is None or empty. Check Railway Variables.")
    raise ValueError("DATABASE_URL environment variable not set. Please set it in Railway.")
# --- AKHIR DEBUGGING ---

engine = create_engine(DATABASE_URL)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine) # Tambahkan ini untuk Flask/SQLAlchemy
Base = declarative_base()

# --- Hapus atau Komen Kode Zona Waktu untuk Sementara ---
# LOCAL_TIMEZONE = datetime.now(pytz.utc).astimezone().tzinfo # Komen/hapus ini
# TIMEZONE_MAP = { ... } # Komen/hapus ini

# --- MODEL DATABASE ---
class Reminder(Base):
    __tablename__ = 'reminders'
    # Untuk SQLite, ID biasanya auto-increment Integer, bukan UUID.
    # Jika tabel sudah ada di Supabase, jangan jalankan create_all lagi setelah ini
    id = Column(Integer, primary_key=True, autoincrement=True) # ID auto-increment untuk SQLite
    user_id = Column(String, default="anonymous") # Bisa tetap string
    text = Column(String, nullable=False)
    reminder_time = Column(DateTime, nullable=False) # Untuk SQLite, tanpa timezone=True
    created_at = Column(DateTime, default=datetime.utcnow) 
    is_completed = Column(Boolean, default=False)
    repeat_type = Column(String, default="none") 
    repeat_interval = Column(Integer, default=0) 

    # ... (metode __repr__ dan to_dict tetap sama, tapi perhatikan reminder_time tanpa tzinfo) ...
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "text": self.text,
            "reminder_time": self.reminder_time.isoformat() if self.reminder_time else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_completed": self.is_completed,
            "repeat_type": self.repeat_type,
            "repeat_interval": self.repeat_interval
        }

# --- FUNGSI NLP: extract_schedule ---
# PENTING: Untuk testing SQLite, pastikan extract_schedule mengembalikan datetime yang *naive* (tanpa tzinfo)
# atau ubah model Reminder agar bisa menyimpan aware datetime di SQLite jika drivernya mendukung.
# Cara termudah: saat ini, pastikan semua datetime yang dihasilkan extract_schedule tidak punya tzinfo
# atau ubah reminder_time=Column(DateTime(timezone=True), nullable=False) menjadi
# reminder_time=Column(DateTime, nullable=False) di model Reminder.
def extract_schedule(text):
    # Dalam implementasi extract_schedule Anda, ganti semua
    # now_local = datetime.now(LOCAL_TIMEZONE)
    # menjadi
    now_local = datetime.now() # Naive datetime
    # dan pastikan setiap .replace() tidak menambahkan tzinfo=...
    # atau hapus semua tzinfo=... dari semua .replace()
    # dan di bagian akhir, pastikan scheduled_datetime_final tidak memiliki tzinfo
    # return {"event": final_event_description, "datetime": scheduled_datetime_final.replace(tzinfo=None), ...}

    # ... (ubah fungsi extract_schedule Anda agar tidak menggunakan TZinfo) ...
    # (contoh bagian akhir extract_schedule)
    scheduled_datetime_final = scheduled_datetime_aware.replace(tzinfo=None) # Pastikan dia naive

    if scheduled_datetime_final < now_local - tolerance: # Perbandingan naive vs naive
        return None
    # ...

# --- Route (Endpoint) untuk Aplikasi Web Anda ---
# ... (tetap sama) ...

# --- Bagian untuk menjalankan Flask App ---
if __name__ == '__main__':
    # Import sa_text for server_default here if not already imported globally
    from sqlalchemy.sql import text as sa_text 
    with engine.connect() as connection:
        Base.metadata.create_all(connection)
    print("Database tables ensured to exist.")
# ...
