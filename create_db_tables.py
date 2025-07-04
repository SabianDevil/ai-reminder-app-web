import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from datetime import datetime
import pytz
from sqlalchemy.sql import text as sa_text
from sqlalchemy import Column, String, DateTime, Boolean, Integer

# --- KONFIGURASI DATABASE ---
DATABASE_URL = os.getenv("DATABASE_URL")

print(f"DEBUG (create_db_tables.py): DATABASE_URL yang diterima: '{DATABASE_URL}'") # Debugging
if not DATABASE_URL:
    print("ERROR (create_db_tables.py): DATABASE_URL environment variable not set. Cannot create tables.")
    raise ValueError("DATABASE_URL environment variable not set. Cannot create tables.")

engine = create_engine(DATABASE_URL)
Base = declarative_base()

# --- MODEL DATABASE (SALIN DARI APP.PY) ---
class Reminder(Base):
    __tablename__ = 'reminders'
    id = Column(String, primary_key=True, server_default=sa_text("gen_random_uuid()")) 
    user_id = Column(String) 
    text = Column(String, nullable=False)
    reminder_time = Column(DateTime(timezone=True), nullable=False) 
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow) 
    is_completed = Column(Boolean, default=False)
    repeat_type = Column(String, default="none") 
    repeat_interval = Column(Integer, default=0) 

    def __repr__(self):
        return f"<Reminder(id='{self.id}', text='{self.text}', time='{self.reminder_time}')>"

# --- FUNGSI UTAMA UNTUK MEMBUAT TABEL ---
if __name__ == '__main__':
    print("INFO (create_db_tables.py): Attempting to create database tables...")
    try:
        Base.metadata.create_all(engine)
        print("INFO (create_db_tables.py): Database tables created successfully or already exist.")
    except Exception as e:
        print(f"FATAL ERROR (create_db_tables.py): Failed to create database tables: {e}")
        raise # Re-raise error agar Railway tahu ada masalah
