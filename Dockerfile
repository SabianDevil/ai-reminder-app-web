# Gunakan image dasar Python 3.11 yang ramping dan berbasis Debian Buster
FROM python:3.11-slim-buster

# Setel direktori kerja di dalam container. Semua perintah berikutnya akan dijalankan dari sini.
WORKDIR /app

# Salin file requirements.txt ke dalam container
COPY requirements.txt .

# Instal dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Salin skrip pembuatan tabel dan semua kode aplikasi Anda ke dalam container
COPY create_db_tables.py .
COPY . . # Ini akan menyalin sisa file, termasuk app.py

# --- PENTING: ATUR DATABASE_URL ANDA DI SINI ---
# Gunakan connection string dari Railway's PostgreSQL Add-on Anda
# Contoh: postgresql://postgres:randompassword@postgres.railway.internal:5432/railway
ENV DATABASE_URL="postgresql://postgres:gzOvIzbczeMoVjSXiKpPmAacWEFJqwPq@postgres.railway.internal:5432/railway"

# Beri tahu Docker bahwa container mendengarkan pada port 5000 (port default Flask)
EXPOSE 5000

# --- LANGKAH BARU: JALANKAN SKRIP PEMBUATAN TABEL SEBELUM START APLIKASI UTAMA ---
# Ini akan memastikan tabel dibuat saat container di-deploy
RUN python create_db_tables.py

# Komando untuk menjalankan aplikasi saat container dimulai (Start Command)
CMD ["python", "app.py"]
