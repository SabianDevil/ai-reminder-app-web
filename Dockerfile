# Gunakan image dasar Python 3.11 yang ramping dan berbasis Debian Buster
FROM python:3.11-slim-buster

# Setel direktori kerja di dalam container. Semua perintah berikutnya akan dijalankan dari sini.
WORKDIR /app

# Salin file requirements.txt ke dalam container
COPY requirements.txt .

# Instal dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua kode aplikasi Anda ke dalam container
COPY . .

# --- PENTING: HAPUS BARIS ENV DATABASE_URL DI SINI ---
# Baris ENV DATABASE_URL="..." harus DIHAPUS atau DIKOMENTARI
# Karena Railway akan menyuntikkan variabel lingkungannya sendiri secara otomatis
# --- AKHIR PENTING ---

# Beri tahu Docker bahwa container mendengarkan pada port 5000
EXPOSE 5000

# Komando untuk menjalankan aplikasi saat container dimulai (Start Command)
CMD ["python", "app.py"]
