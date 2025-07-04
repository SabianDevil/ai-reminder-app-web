# Gunakan image dasar Python 3.11 yang ramping dan berbasis Debian Buster
FROM python:3.11-slim-buster

# Setel direktori kerja di dalam container. Semua perintah berikutnya akan dijalankan dari sini.
WORKDIR /app

# Salin file requirements.txt
COPY requirements.txt .

# Instal dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Salin skrip pembuatan tabel dan semua kode aplikasi Anda ke dalam container
COPY create_db_tables.py .
COPY app.py .
COPY templates/ templates/
COPY static/ static/

# --- PERBAIKAN PENTING DI SINI: PASTIKAN DATABASE_URL TERSEDIA UNTUK RUN ---
# Gunakan ARG untuk menerima URL selama build
ARG DATABASE_URL_ARG

# Setel DATABASE_URL sebagai ENV variabel. Ini akan tersedia untuk perintah RUN berikutnya
# Jika DATABASE_URL_ARG kosong, Railway akan menggunakan DATABASE_URL dari variable di dashboard
# Jika tidak kosong, gunakan DATABASE_URL_ARG
ENV DATABASE_URL=${DATABASE_URL_ARG}
# --- AKHIR PERBAIKAN ---

# Beri tahu Docker bahwa container mendengarkan pada port 5000 (port default Flask)
EXPOSE 5000

# --- JALANKAN SKRIP PEMBUATAN TABEL SEBELUM START APLIKASI UTAMA ---
# Sekarang skrip ini akan memiliki DATABASE_URL di lingkungannya
RUN python create_db_tables.py

# Komando untuk menjalankan aplikasi saat container dimulai (Start Command)
CMD ["python", "app.py"]
