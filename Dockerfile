# Gunakan image dasar Python 3.11 yang ramping dan berbasis Debian Buster
FROM python:3.11-slim-buster

# Setel direktori kerja di dalam container
WORKDIR /app

# Salin file requirements.txt ke dalam container
COPY requirements.txt .

# Instal dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua kode aplikasi Anda ke dalam container
COPY . .

# --- PERBAIKAN SANGAT PENTING DI SINI ---
# WARNING: Ini TIDAK DIREKOMENDASIKAN untuk PRODUKSI karena mengekspos password.
# Namun, ini adalah cara terakhir untuk mengatasi masalah ArgumentError yang persisten.
ENV DATABASE_URL="postgresql://postgres:SabianGBA2@db.hckxsojwnwjygszahllc.supabase.co:5432/postgres"
# --- AKHIR PERBAIKAN SANGAT PENTING ---

# Komando untuk menjalankan aplikasi (Start Command)
CMD ["python", "app.py"]

# Atur port yang akan didengarkan oleh aplikasi Anda
EXPOSE 5000
