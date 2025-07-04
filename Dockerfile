# Gunakan image dasar Python 3.11 yang ramping dan berbasis Debian Buster
FROM python:3.11-slim-buster

# Setel direktori kerja di dalam container. Semua perintah berikutnya akan dijalankan dari sini.
WORKDIR /app

# Salin file requirements.txt
COPY requirements.txt .

# Instal dependensi
RUN pip install --no-cache-dir -r requirements.txt

# --- PERBAIKAN SANGAT PENTING DI SINI: Salin file satu per satu ---
COPY app.py .
COPY create_db_tables.py .
COPY templates/ templates/
COPY static/ static/
# --- AKHIR PERBAIKAN ---

# --- PENTING: ATUR DATABASE_URL ANDA DI SINI ---
# Gunakan connection string dari Railway's PostgreSQL Add-on Anda
# Contoh: postgresql://postgres:randompassword@postgres.railway.internal:5432/railway
ENV DATABASE_URL="postgresql://postgres:gzOvIzbczeMoVjSXiKpPmAacWEFJqwPq@postgres.railway.internal:5432/railway"

# Beri tahu Docker bahwa container mendengarkan pada port 5000 (port default Flask)
EXPOSE 5000

# Komando untuk menjalankan aplikasi saat container dimulai (Start Command)
CMD ["python", "app.py"]
