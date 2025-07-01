document.addEventListener('DOMContentLoaded', () => {
    const reminderInput = document.getElementById('reminderInput');
    const addReminderBtn = document.getElementById('addReminderBtn');
    const reminderList = document.getElementById('reminderList');
    const messageArea = document.getElementById('messageArea');
    const calendarEl = document.getElementById('calendar'); // Ambil wadah FullCalendar

    let calendar; // Deklarasikan variabel untuk instance FullCalendar

    // --- Fungsi Jam Zona Waktu ---
    const timezoneOffsets = { // Offset dalam jam dari UTC
        "Lokal": (new Date().getTimezoneOffset() / -60), // Mendapatkan offset lokal dari UTC
        "WIB": 7, // UTC+7
        "WITA": 8, // UTC+8
        "WIT": 9  // UTC+9
    };

    function updateClocks() {
        const now = new Date(); // Waktu lokal komputer

        for (const tzLabel in timezoneOffsets) {
            const offset = timezoneOffsets[tzLabel];
            // Hitung UTC time: now.getTime() - (now.getTimezoneOffset() * 60000)
            // Kemudian tambahkan offset TZ target
            const targetTime = new Date(now.getTime() + (offset * 3600000) - (now.getTimezoneOffset() * 60000));
            
            const hours = targetTime.getHours().toString().padStart(2, '0');
            const minutes = targetTime.getMinutes().toString().padStart(2, '0');
            const seconds = targetTime.getSeconds().toString().padStart(2, '0');
            
            const clockElement = document.getElementById(`${tzLabel.toLowerCase()}Clock`);
            if (clockElement) {
                clockElement.textContent = `${hours}:${minutes}:${seconds}`;
            } else if (tzLabel === "Lokal") { // Handle for "Lokal" clock specifically
                document.getElementById('localClock').textContent = `${hours}:${minutes}:${seconds}`;
            }
        }
    }

    // Perbarui jam setiap detik
    setInterval(updateClocks, 1000);
    updateClocks(); // Panggil sekali saat start

    // --- Fungsi Utilitas ---
    function showMessage(message, type) {
        messageArea.textContent = message;
        messageArea.className = `message-area visible ${type}`;
        if (type === 'success') {
            setTimeout(() => {
                messageArea.classList.remove('visible');
            }, 5000);
        }
    }

    // --- Inisialisasi FullCalendar ---
    function initializeCalendar(reminders) {
        if (calendar) { // Hancurkan instance kalender sebelumnya jika ada
            calendar.destroy();
        }

        const events = reminders.map(r => ({
            id: r.id,
            title: r.text,
            start: r.reminder_time, // FullCalendar bisa langsung pakai ISO string
            allDay: false, // Karena ada waktu spesifik
            display: 'auto', // Tampilkan sebagai event biasa
            backgroundColor: r.is_completed ? 'grey' : 'red', // Warna event di kalender
            borderColor: r.is_completed ? 'grey' : 'red',
            extendedProps: {
                repeatType: r.repeat_type,
                repeatInterval: r.repeat_interval,
                isCompleted: r.is_completed
            }
        }));

        calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth', // Tampilan awal bulan
            locale: 'id', // Set bahasa ke Indonesia
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            events: events, // Berikan event yang sudah kita siapkan
            eventDidMount: function(info) {
                // Ini adalah callback ketika event dirender
                // Anda bisa menambahkan custom dot/flag di sini jika default FullCalendar tidak cukup
                if (info.event.extendedProps.isCompleted) {
                    info.el.style.backgroundColor = 'grey'; // Jika selesai, warna abu-abu
                    info.el.style.borderColor = 'grey';
                } else {
                    info.el.style.backgroundColor = 'red'; // Default merah untuk aktif
                    info.el.style.borderColor = 'red';
                }
            },
            eventClick: function(info) {
                // Contoh: Ketika event di kalender diklik
                const reminder = info.event.extendedProps;
                let repeatInfo = "";
                if (reminder.repeatType === 'yearly') {
                    repeatInfo = "(Setiap Tahun)";
                    if (reminder.repeatInterval > 1) {
                        repeatInfo = `(Setiap ${reminder.repeatInterval} Tahun)`;
                    }
                } else if (reminder.repeatType === 'monthly_interval') {
                    repeatInfo = `(Setiap ${reminder.repeatInterval} Bulan)`;
                }

                const completedStatus = reminder.isCompleted ? 'Sudah selesai.' : 'Belum selesai.';

                alert(`Pengingat: ${info.event.title}\nWaktu: ${info.event.start.toLocaleString('id-ID', { timeZoneName: 'short' })}\nPengulangan: ${repeatInfo || 'Tidak ada'}\nStatus: ${completedStatus}`);
            },
            // Anda bisa tambahkan konfigurasi lain untuk kustomisasi tampilan
            // Misalnya untuk tampilan hari ini, akhir pekan, dll.
            // FullCalendar secara otomatis menyesuaikan dengan tema gelap melalui CSS yang kita buat
        });
        calendar.render();
    }

    // --- Fungsi Interaksi Backend ---
    async function loadReminders() {
        reminderList.innerHTML = '<li>Memuat pengingat...</li>';
        calendarEl.innerHTML = '<p>Memuat kalender...</p>'; // Tampilkan loading untuk kalender

        try {
            const response = await fetch('/get_reminders');
            const reminders = await response.json();

            reminderList.innerHTML = ''; // Hapus item yang ada

            if (reminders.length === 0) {
                reminderList.innerHTML = '<li>Belum ada pengingat terjadwal.</li>';
            } else {
                reminders.forEach(reminder => {
                    const listItem = document.createElement('li');
                    // reminder_time_display sudah diformat di backend
                    listItem.textContent = reminder.reminder_time_display + ' - ' + reminder.text;
                    
                    if (reminder.repeat_type && reminder.repeat_type !== 'none') {
                        let repeatInfo = `(${reminder.repeat_type.charAt(0).toUpperCase() + reminder.repeat_type.slice(1)})`;
                        if (reminder.repeat_type === 'monthly_interval' && reminder.repeat_interval > 0) {
                            repeatInfo = `(Setiap ${reminder.repeat_interval} Bulan)`;
                        } else if (reminder.repeat_type === 'yearly' && reminder.repeat_interval > 1) {
                            repeatInfo = `(Setiap ${reminder.repeat_interval} Tahun)`;
                        } else if (reminder.repeat_type === 'yearly' && reminder.repeat_interval === 1) {
                            repeatInfo = `(Setiap Tahun)`;
                        }
                        listItem.textContent += ` ${repeatInfo}`;
                    }

                    if (reminder.is_completed) {
                        listItem.style.textDecoration = 'line-through';
                        listItem.style.color = '#888';
                        listItem.textContent += ' (Selesai)';
                    }
                    reminderList.appendChild(listItem);
                });
            }

            // Inisialisasi atau perbarui kalender dengan data yang dimuat
            initializeCalendar(reminders);

        } catch (error) {
            console.error('Error loading reminders:', error);
            showMessage('Gagal memuat pengingat. Cek koneksi server.', 'error');
            calendarEl.innerHTML = '<p>Gagal memuat kalender.</p>';
        }
    }

    // Fungsi untuk menambahkan pengingat
    addReminderBtn.addEventListener('click', async () => {
        const reminderText = reminderInput.value.trim();

        if (!reminderText) {
            showMessage('Mohon masukkan catatan jadwal.', 'error');
            return;
        }

        addReminderBtn.disabled = true;
        addReminderBtn.textContent = 'Menambahkan...';

        try {
            const response = await fetch('/add_reminder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: reminderText }),
            });

            const result = await response.json();

            if (response.ok) {
                showMessage(result.message, 'success');
                reminderInput.value = '';
                loadReminders(); // Muat ulang pengingat dan kalender
            } else {
                showMessage(`Error: ${result.error || 'Terjadi kesalahan.'}`, 'error');
            }
        } catch (error) {
            console.error('Error adding reminder:', error);
            showMessage('Gagal terhubung ke server. Cek koneksi.', 'error');
        } finally {
            addReminderBtn.disabled = false;
            addReminderBtn.textContent = 'Tambah Pengingat';
        }
    });

    // Panggil saat halaman dimuat
    loadReminders();
});