# Gunakan image dasar Python
FROM python:3.11-slim-buster

# Setel direktori kerja di dalam container
WORKDIR /app

# Salin file requirements.txt ke dalam container
COPY requirements.txt .

# Instal dependensi
RUN pip install --no-cache-dir -r requirements.txt

# Salin semua kode aplikasi Anda ke dalam container
COPY . .

# Komando untuk menjalankan aplikasi (Start Command)
CMD ["python", "app.py"]

# Atur port yang akan didengarkan oleh aplikasi Anda
EXPOSE 5000
