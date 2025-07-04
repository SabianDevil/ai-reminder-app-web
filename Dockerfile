# --- PERBAIKAN PENTING DI SINI ---
# Gunakan image dasar Python 3.9 yang lebih stabil dan teruji
FROM python:3.9-slim-buster
# --- AKHIR PERBAIKAN ---

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

# Gunakan ARG untuk menerima DATABASE_URL selama build
ARG DATABASE_URL_ARG

# Setel DATABASE_URL sebagai ENV variabel untuk runtime dan untuk perintah RUN berikutnya
ENV DATABASE_URL=$DATABASE_URL_ARG

# Beri tahu Docker bahwa container mendengarkan pada port 5000 (port default Flask)
EXPOSE 5000

# JALANKAN SKRIP PEMBUATAN TABEL SEBELUM START APLIKASI UTAMA
RUN python create_db_tables.py

# Komando untuk menjalankan aplikasi saat container dimulai (Start Command)
CMD ["python", "app.py"]
