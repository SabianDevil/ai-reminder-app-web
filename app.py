import os
from flask import Flask, render_template

# --- Inisialisasi Aplikasi Flask ---
app = Flask(__name__)

# --- Route untuk Halaman Utama ---
@app.route('/')
def index():
    # Ini akan menyajikan file index.html dari folder 'templates'
    return render_template('index.html')

# --- Bagian untuk menjalankan Flask App ---
if __name__ == '__main__':
    # Mode debug akan memberikan pesan error lebih detail di log
    # host='0.0.0.0' agar bisa diakses dari luar localhost (misalnya dari ponsel di jaringan yang sama)
    app.run(debug=True, host='0.0.0.0')
