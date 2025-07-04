# Gunakan image dasar Python 3.11 yang ramping dan berbasis Debian Buster
FROM python:3.11-slim-buster

# Setel direktori kerja di dalam container. Semua perintah berikutnya akan dijalankan dari sini.
WORKDIR /app

# Salin file requirements.txt
COPY requirements.txt .

# Instal dependensi
RUN pip install --no-cache-dir -r requirements.txt

# --- PERBAIKAN PENTING DI SINI ---
# Deklarasikan ARG untuk menerima DATABASE_URL selama build
ARG DATABASE_URL

# Setel DATABASE_URL sebagai ENV variabel untuk runtime dan untuk perintah RUN berikutnya
# Ini akan memastikan DATABASE_URL tersedia saat create_db_tables.py dijalankan
ENV DATABASE_URL=$DATABASE_URL

# Salin skrip pembuatan tabel dan semua kode aplikasi Anda ke dalam container
COPY create_db_tables.py .
COPY app.py .
COPY templates/ templates/
COPY static/ static/
# --- AKHIR PERBAIKAN ---

# Beri tahu Docker bahwa container mendengarkan pada port 5000 (port default Flask)
EXPOSE 5000

# --- LANGKAH BARU: JALANKAN SKRIP PEMBUATAN TABEL SEBELUM START APLIKASI UTAMA ---
# Ini akan memastikan tabel dibuat saat container di-deploy
RUN python create_db_tables.py

# Komando untuk menjalankan aplikasi saat container dimulai (Start Command)
CMD ["python", "app.py"]
