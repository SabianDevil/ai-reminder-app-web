# Gunakan image dasar Python 3.11 yang ramping dan berbasis Debian Buster
FROM python:3.11-slim-buster

# Setel direktori kerja di dalam container. Semua perintah berikutnya akan dijalankan dari sini.
WORKDIR /app

# Salin file requirements.txt ke dalam container
# File ini harus ada di root folder GitHub Anda
COPY requirements.txt .

# Instal semua dependensi Python. --no-cache-dir untuk mengurangi ukuran image.
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua kode aplikasi Anda dari folder lokal ke dalam container
# Titik pertama (.) merujuk ke direktori saat ini di host (lokal Anda)
# Titik kedua (.) merujuk ke direktori kerja di dalam container (/app)
COPY . .

# --- PENTING: ATUR DATABASE_URL ANDA DI SINI ---
# Ganti placeholder dengan connection string Supabase Anda yang sudah di-URL encode
# Contoh: postgresql://postgres:%40SabianGBA2@db.hckxsojwnwjygszahllc.supabase.co:5432/postgres
# Anda harus mengambil string ini PERSIS dari output console Python Anda sebelumnya.
ENV DATABASE_URL="postgresql://postgres:SabianGBA2@db.hckxsojwnwjygszahllc.supabase.co:5432/postgres"

# Beri tahu Docker bahwa container mendengarkan pada port 5000 (port default Flask)
EXPOSE 5000

# Komando untuk menjalankan aplikasi saat container dimulai (Start Command)
# Ini adalah yang akan Railway jalankan untuk memulai server Flask Anda
CMD ["python", "app.py"]
