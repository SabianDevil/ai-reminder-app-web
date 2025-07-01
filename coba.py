import tkinter as tk
from tkinter import messagebox # Modul untuk menampilkan pop-up pesan

# 1. Membuat jendela utama aplikasi
root = tk.Tk()
root.title("Aplikasi Tkinter Pertama Saya") # Mengatur judul jendela
root.geometry("400x300") # Mengatur ukuran jendela (lebar x tinggi)

# 2. Membuat Widget Label
# Label untuk menampilkan teks statis
label_salam = tk.Label(root, text="Halo, Tkinter! Selamat datang di aplikasi GUI Anda.")
label_salam.pack(pady=20) # Menempatkan label di jendela dengan sedikit padding vertikal

# 3. Membuat Widget Entry (input satu baris)
label_nama = tk.Label(root, text="Masukkan nama Anda:")
label_nama.pack()

entry_nama = tk.Entry(root, width=30)
entry_nama.pack(pady=5)

# 4. Membuat Fungsi yang akan dijalankan saat tombol diklik
def tampilkan_pesan():
    nama = entry_nama.get() # Mengambil teks dari widget Entry
    if nama:
        messagebox.showinfo("Pesan", f"Halo, {nama}! Senang bertemu denganmu.")
    else:
        messagebox.showwarning("Peringatan", "Nama tidak boleh kosong!")

# 5. Membuat Widget Button
# Tombol yang akan memanggil fungsi 'tampilkan_pesan' saat diklik
tombol_sapa = tk.Button(root, text="Sapa Saya", command=tampilkan_pesan)
tombol_sapa.pack(pady=10)

# 6. Menjalankan loop utama aplikasi
# Ini harus selalu ada di akhir kode Tkinter Anda
root.mainloop()