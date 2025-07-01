import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import re
from plyer import notification
from tkcalendar import Calendar
import pytz

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

TIMEZONE_MAP = {
    "wib": "Asia/Jakarta",
    "wita": "Asia/Makassar",
    "wit": "Asia/Jayapura",
    "est": "America/New_York",
    "pst": "America/Los_Angeles",
    "gmt": "Etc/GMT",
    "utc": "Etc/UTC",
    "gmt+7": "Etc/GMT-7",
    "gmt-7": "Etc/GMT+7"
}

LOCAL_TIMEZONE = datetime.now(pytz.utc).astimezone().tzinfo

class ReminderApp:
    def __init__(self, master):
        self.master = master
        master.title("AI Pengingat Pribadi")
        master.geometry("800x650")
        master.resizable(False, False)

        self.main_frame = ctk.CTkFrame(master)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.left_frame = ctk.CTkFrame(self.main_frame)
        self.left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.label_input = ctk.CTkLabel(self.left_frame, text="Masukkan catatan jadwal Anda di bawah:", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_input.pack(pady=(15, 5))

        self.text_input = ctk.CTkTextbox(self.left_frame, height=7, width=350, font=("Arial", 11))
        self.text_input.pack(pady=5)

        self.add_button = ctk.CTkButton(self.left_frame, text="Tambah Pengingat", command=self.add_reminder, font=ctk.CTkFont(size=11, weight="bold"),
                                        hover_color="#3A7FB0")
        self.add_button.pack(pady=10)

        self.label_list = ctk.CTkLabel(self.left_frame, text="Daftar Pengingat Mendatang:", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_list.pack(pady=(15, 5))

        self.scrollable_frame = ctk.CTkScrollableFrame(self.left_frame, width=350, height=200)
        self.scrollable_frame.pack(pady=5, fill="both", expand=True)

        self.scheduled_reminders = []
        self.reminder_labels = {}
        self.calendar_event_ids = []

        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.label_calendar = ctk.CTkLabel(self.right_frame, text="Lihat Jadwal di Kalender:", font=ctk.CTkFont(size=12, weight="bold"))
        self.label_calendar.pack(pady=(15, 5))

        self.cal = Calendar(self.right_frame, selectmode='day',
                            year=datetime.now().year, month=datetime.now().month, day=datetime.now().day,
                            date_pattern='dd/mm/yyyy',
                            background="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "white",
                            foreground="white" if ctk.get_appearance_mode() == "Dark" else "black",
                            normalbackground="#343638" if ctk.get_appearance_mode() == "Dark" else "#f0f0f0",
                            weekendbackground="#343638" if ctk.get_appearance_mode() == "Dark" else "#f0f0f0",
                            othermonthbackground="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "white",
                            othermonthforeground="gray",
                            headersbackground="#2b2b2b" if ctk.get_appearance_mode() == "Dark" else "white",
                            headersforeground="white" if ctk.get_appearance_mode() == "Dark" else "black",
                            selectbackground="#1F6AA5",
                            selectforeground="white",
                            bordercolor="#1F6AA5",
                            font=("Arial", 10))
        self.cal.pack(pady=10, fill="both", expand=True)

        self.cal.bind("<<CalendarSelected>>", self.show_reminders_for_selected_date)

        self.selected_date_reminders_frame = ctk.CTkScrollableFrame(self.right_frame, width=350, height=150)
        self.selected_date_reminders_frame.pack(pady=5, fill="both", expand=True)
        ctk.CTkLabel(self.selected_date_reminders_frame, text="Pilih tanggal di kalender untuk melihat jadwal.", text_color="gray").pack(pady=5)

        self.update_calendar_events()
        self.check_reminders_loop()
        self.update_reminder_list()

    def extract_schedule(self, text):
        original_text = text.lower()
        processed_text = original_text
        
        now_local = datetime.now(LOCAL_TIMEZONE) 
        scheduled_datetime_aware = now_local 
        
        target_tz = LOCAL_TIMEZONE 
        tz_matched = False
        tz_pattern_parts = [re.escape(k) for k in TIMEZONE_MAP.keys()]
        tz_pattern = r'\b(' + '|'.join(tz_pattern_parts) + r')\b'
        
        tz_match = re.search(tz_pattern, processed_text, re.IGNORECASE)
        if tz_match:
            tz_abbr = tz_match.group(1).lower()
            try:
                target_tz = pytz.timezone(TIMEZONE_MAP[tz_abbr])
                processed_text = processed_text.replace(tz_match.group(0), '').strip() 
                tz_matched = True
            except pytz.UnknownTimeZoneError:
                pass 
        
        repeat_type = "none"
        repeat_interval = 0
        default_hour, default_minute = 9, 0

        monthly_repeat_pattern = r'(?:setiap|tiap)\s*(\d+)\s*bulan|(?:(\d+)\s*bulan\s*kedepan)'
        monthly_repeat_match = re.search(monthly_repeat_pattern, processed_text)
        if monthly_repeat_match:
            repeat_type = "monthly_interval"
            if monthly_repeat_match.group(1):
                repeat_interval = int(monthly_repeat_match.group(1))
            elif monthly_repeat_match.group(2):
                repeat_interval = int(monthly_repeat_match.group(2))
            processed_text = re.sub(monthly_repeat_pattern, '', processed_text).strip()

        yearly_repeat_pattern_explicit = r'(?:setiap|tiap)\s*(\d+)\s*tahun|(?:(\d+)\s*tahun\s*kedepan)'
        yearly_repeat_match_explicit = re.search(yearly_repeat_pattern_explicit, processed_text)
        if yearly_repeat_match_explicit:
            repeat_type = "yearly"
            if yearly_repeat_match_explicit.group(1):
                repeat_interval = int(yearly_repeat_match_explicit.group(1))
            elif yearly_repeat_match_explicit.group(2):
                repeat_interval = int(yearly_repeat_match_explicit.group(2))
            processed_text = re.sub(yearly_repeat_pattern_explicit, '', processed_text).strip()
        elif "setiap tahun" in processed_text or "tiap tahun" in processed_text:
            repeat_type = "yearly"
            repeat_interval = 1 
            processed_text = processed_text.replace("setiap tahun", "").replace("tiap tahun", "").strip()
        
        if repeat_type == "monthly_interval" and ("tahun" in original_text or "yearly" in original_text):
            monthly_repeat_match = None
            repeat_type = "none"
            repeat_interval = 0

        found_explicit_date = False

        date_keywords_map = {
            "hari ini": now_local.date(),
            "besok": (now_local + timedelta(days=1)).date(),
            "lusa": (now_local + timedelta(days=2)).date(),
            "minggu depan": (now_local + timedelta(weeks=1)).date(),
            "bulan depan": (now_local.replace(day=1) + timedelta(days=32)).replace(day=now_local.day).date()
        }
        
        for keyword, date_obj in date_keywords_map.items():
            if keyword in processed_text:
                scheduled_datetime_aware = scheduled_datetime_aware.replace(year=date_obj.year, month=date_obj.month, day=date_obj.day, tzinfo=scheduled_datetime_aware.tzinfo)
                processed_text = processed_text.replace(keyword, '').strip()
                found_explicit_date = True
                break
        
        day_of_week_map = {
            "senin": 0, "selasa": 1, "rabu": 2, "kamis": 3, "jumat": 4, "sabtu": 5, "minggu": 6
        }
        if not found_explicit_date:
            for day_name, day_num in day_of_week_map.items():
                if f"minggu depan {day_name}" in processed_text or f"depan {day_name}" in processed_text:
                    days_ahead = (day_num - now_local.weekday() + 7) % 7 + 7
                    if days_ahead == 0: days_ahead = 7
                    target_date = now_local.date() + timedelta(days=days_ahead)
                    scheduled_datetime_aware = scheduled_datetime_aware.replace(year=target_date.year, month=target_date.month, day=target_date.day, tzinfo=scheduled_datetime_aware.tzinfo)
                    processed_text = processed_text.replace(f"minggu depan {day_name}", "").replace(f"depan {day_name}", "").strip()
                    found_explicit_date = True
                    break
                elif day_name in processed_text:
                    days_ahead = (day_num - now_local.weekday() + 7) % 7
                    if days_ahead == 0: days_ahead = 7
                    target_date = now_local.date() + timedelta(days=days_ahead)
                    scheduled_datetime_aware = scheduled_datetime_aware.replace(year=target_date.year, month=target_date.month, day=target_date.day, tzinfo=scheduled_datetime_aware.tzinfo)
                    processed_text = processed_text.replace(day_name, "").strip()
                    found_explicit_date = True
                    
        if not found_explicit_date:
            date_pattern = r'\b(\d{1,2}) (januari|februari|maret|april|mei|juni|juli|agustus|september|oktober|november|desember) (\d{4})\b|\b(\d{1,2})/(\d{1,2})/(\d{4})\b'
            found_date_match = re.search(date_pattern, processed_text, re.IGNORECASE)
            if found_date_match:
                try:
                    parsed_date = None
                    if found_date_match.group(2):
                        day_str, month_name, year_str = found_date_match.group(1, 2, 3)
                        bulan_map = {
                            "januari": 1, "februari": 2, "maret": 3, "april": 4, "mei": 5, "juni": 6,
                            "juli": 7, "agustus": 8, "september": 9, "oktober": 10, "november": 11, "desember": 12
                        }
                        month_num = bulan_map.get(month_name.lower())
                        if month_num:
                            parsed_date = datetime(int(year_str), month_num, int(day_str)).date()
                    elif found_date_match.group(4):
                        day_str, month_str, year_str = found_date_match.group(4, 5, 6)
                        parsed_date = datetime(int(year_str), int(month_str), int(day_str)).date()

                    if parsed_date:
                        scheduled_datetime_aware = scheduled_datetime_aware.replace(year=parsed_date.year, month=parsed_date.month, day=parsed_date.day, tzinfo=scheduled_datetime_aware.tzinfo)
                        processed_text = re.sub(date_pattern, '', processed_text, flags=re.IGNORECASE).strip()
                        found_explicit_date = True
                except (ValueError, TypeError):
                    pass
        
        found_time_set_by_match = False

        relative_time_pattern = r'\b(dalam\s+)?(\d+)\s*(jam|menit)\s*(lagi|ke\s+depan)?\b'
        relative_time_match = re.search(relative_time_pattern, processed_text, re.IGNORECASE)
        if relative_time_match:
            value = int(relative_time_match.group(2))
            unit = relative_time_match.group(3)
            
            if unit == "jam":
                scheduled_datetime_aware = now_local + timedelta(hours=value)
            elif unit == "menit":
                scheduled_datetime_aware = now_local + timedelta(minutes=value)
            
            found_time_set_by_match = True
            processed_text = re.sub(relative_time_pattern, '', processed_text, flags=re.IGNORECASE).strip()
        
        waktu_sholat_map = {
            "subuh": "05:00",
            "dzuhur": "12:00",
            "ashar": "15:00",
            "maghrib": "18:00",
            "isya": "19:30"
        }
        
        if not found_time_set_by_match:
            for sholat_name, sholat_time_str in waktu_sholat_map.items():
                if f"setelah {sholat_name}" in processed_text or sholat_name in processed_text:
                    try:
                        hour, minute = map(int, sholat_time_str.split(':'))
                        temp_time = scheduled_datetime_aware.replace(hour=hour, minute=minute, second=0, microsecond=0, tzinfo=scheduled_datetime_aware.tzinfo)
                        if f"setelah {sholat_name}" in processed_text:
                            temp_time += timedelta(minutes=30)
                        
                        if temp_time < now_local and temp_time.date() == scheduled_datetime_aware.date():
                            temp_time += timedelta(days=1)

                        scheduled_datetime_aware = temp_time
                        found_time_set_by_match = True
                        processed_text = processed_text.replace(f"setelah {sholat_name}", "").replace(sholat_name, "").strip()
                        break
                    except ValueError:
                        pass

        if not found_time_set_by_match:
            time_pattern = r'\b(jam |pukul )?(\d{1,2}([\.:]\d{2})?)\s*(pagi|siang|sore|malam|am|pm)?\b'
            found_time_match = re.search(time_pattern, processed_text, re.IGNORECASE)

            if found_time_match:
                try:
                    time_str_raw = found_time_match.group(2)
                    ampm_str = (found_time_match.group(4) or '').lower()

                    hour_extracted = 0
                    minute_extracted = 0

                    if ':' in time_str_raw:
                        hour_extracted, minute_extracted = map(int, time_str_raw.split(':'))
                    elif '.' in time_str_raw:
                        hour_extracted, minute_extracted = map(int, time_str_raw.split('.'))
                    else:
                        hour_extracted = int(time_str_raw)
                        
                    if 'pagi' in ampm_str:
                        if hour_extracted == 12: hour_extracted = 0
                    elif 'siang' in ampm_str:
                        if hour_extracted < 12: hour_extracted += 12
                    elif 'sore' in ampm_str or 'pm' in ampm_str:
                        if hour_extracted < 12: hour_extracted += 12
                    elif 'malam' in ampm_str:
                        if hour_extracted < 12: hour_extracted += 12
                        if hour_extracted == 24: hour_extracted = 0
                        
                    if not (0 <= hour_extracted <= 23 and 0 <= minute_extracted <= 59):
                        raise ValueError("Invalid time")
                    
                    temp_time = scheduled_datetime_aware.replace(hour=hour_extracted, minute=minute_extracted, second=0, microsecond=0, tzinfo=scheduled_datetime_aware.tzinfo)
                    
                    if temp_time < now_local and temp_time.date() == scheduled_datetime_aware.date():
                        temp_time += timedelta(days=1)

                    scheduled_datetime_aware = temp_time
                    found_time_set_by_match = True
                    
                    processed_text = re.sub(time_pattern, '', processed_text, flags=re.IGNORECASE).strip()
                except (ValueError, TypeError):
                    pass

        if not found_time_set_by_match:
            temp_time = scheduled_datetime_aware.replace(hour=default_hour, minute=default_minute, second=0, microsecond=0, tzinfo=scheduled_datetime_aware.tzinfo)
            if temp_time < now_local and temp_time.date() == scheduled_datetime_aware.date():
                temp_time += timedelta(days=1)
            scheduled_datetime_aware = temp_time


        # 4. Ekstraksi Deskripsi Event
        stopwords = ['ingatkan', 'saya', 'untuk', 'pada', 'di', 'tanggal', 'pukul', 'jam', 'paling lambat', 'mengingatkan', 'setelah', 'depan', 'setiap', 'tiap', 'ke depan', 'menit', 'lagi', 'dalam', 'kedepan']
        words = processed_text.split()
        final_event_description = ' '.join([word for word in words if word.lower() not in stopwords])
        final_event_description = final_event_description.replace("  ", " ").strip()

        if not final_event_description:
            final_event_description = "Pengingat"


        # 5. Validasi Akhir dan Konversi Zona Waktu
        tolerance = timedelta(seconds=2)
        
        if tz_matched: 
            scheduled_datetime_naive_temp = scheduled_datetime_aware.replace(tzinfo=None)
            scheduled_datetime_localized_target = target_tz.localize(scheduled_datetime_naive_temp)
            scheduled_datetime_final = scheduled_datetime_localized_target.astimezone(LOCAL_TIMEZONE)
        else:
            scheduled_datetime_final = scheduled_datetime_aware 

        if scheduled_datetime_final < now_local - tolerance:
            return None
        
        if scheduled_datetime_final:
            return {"event": final_event_description, "datetime": scheduled_datetime_final, "repeat_type": repeat_type, "repeat_interval": repeat_interval}
        return None

    def format_timezone_display(self, dt_object):
        """Membantu memformat tampilan zona waktu agar lebih ringkas."""
        tz_name_full = dt_object.tzname()
        if tz_name_full:
            if "Western Indonesia Standard Time" in tz_name_full:
                return "WIB"
            elif "Central Indonesia Standard Time" in tz_name_full:
                return "WITA"
            elif "Eastern Indonesia Standard Time" in tz_name_full:
                return "WIT"
            # Jika bukan salah satu dari di atas (misal EST, GMT, dll),
            # dan ingin menampilkan offset numerik pendek, gunakan '%z'.
            # Jika ingin menghilangkan total, kembalikan string kosong.
            # Contoh di sini: Jika bukan WIB/WITA/WIT, akan dihilangkan.
            return "" 
        return "" 

    def add_reminder(self):
        note = self.text_input.get("0.0", "end").strip()
        if not note:
            messagebox.showwarning("Input Kosong", "Mohon masukkan catatan jadwal.")
            return

        extracted_info = self.extract_schedule(note)

        if extracted_info:
            event = extracted_info['event']
            scheduled_time = extracted_info['datetime'] 
            repeat_type = extracted_info['repeat_type']
            repeat_interval = extracted_info['repeat_interval']

            self.scheduled_reminders.append({
                "event": event,
                "datetime": scheduled_time,
                "notified": False,
                "repeat_type": repeat_type,
                "repeat_interval": repeat_interval
            })
            self.scheduled_reminders.sort(key=lambda x: x['datetime'])

            self.update_reminder_list()
            self.update_calendar_events()
            
            tz_display = self.format_timezone_display(scheduled_time)
            if tz_display:
                formatted_time_str = scheduled_time.strftime(f'%d %B %Y %H:%M {tz_display}')
            else:
                formatted_time_str = scheduled_time.strftime('%d %B %Y %H:%M')

            messagebox.showinfo("Sukses!", f"Pengingat untuk '{event}' pada {formatted_time_str} berhasil ditambahkan.")
            self.text_input.delete("0.0", "end")
        else:
            messagebox.showerror("Gagal", "Tidak dapat mendeteksi jadwal dari catatan Anda. Coba format lain atau sertakan tanggal dan waktu yang jelas.")

    def update_reminder_list(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.reminder_labels.clear()

        upcoming_reminders = [r for r in self.scheduled_reminders if not r['notified'] or r['repeat_type'] != 'none']

        if not upcoming_reminders:
            ctk.CTkLabel(self.scrollable_frame, text="Belum ada pengingat terjadwal.", text_color="gray").pack(pady=5)
            return

        for i, reminder in enumerate(upcoming_reminders):
            text_color = "white" if ctk.get_appearance_mode() == "Dark" else "black"
            
            reminder_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
            reminder_frame.pack(fill="x", pady=2, padx=5)

            repeat_info = ""
            if reminder['repeat_type'] == 'yearly':
                repeat_info = "(Setiap Tahun)"
                if reminder['repeat_interval'] > 1:
                    repeat_info = f"(Setiap {reminder['repeat_interval']} Tahun)"
            elif reminder['repeat_type'] == 'monthly_interval':
                repeat_info = f"(Setiap {reminder['repeat_interval']} Bulan)"

            tz_display = self.format_timezone_display(reminder['datetime'])
            if tz_display:
                reminder_date_time_str = reminder['datetime'].strftime(f'%d %B %Y %H:%M {tz_display}')
            else:
                reminder_date_time_str = reminder['datetime'].strftime('%d %B %Y %H:%M')

            reminder_text = f"{reminder_date_time_str} - {reminder['event']} {repeat_info}"
            label = ctk.CTkLabel(reminder_frame, text=reminder_text, anchor="w", justify="left", font=("Arial", 11))
            label.pack(side="left", fill="x", expand=True, padx=5)
            
            self.reminder_labels[i] = label 

    def update_calendar_events(self):
        for event_id in self.calendar_event_ids:
            self.cal.calevent_remove(event_id)
        self.calendar_event_ids.clear()

        for reminder in self.scheduled_reminders:
            date_to_mark = reminder['datetime'].date()
            if not reminder['notified'] or reminder['repeat_type'] != 'none':
                event_id = self.cal.calevent_create(date_to_mark, reminder['event'], 'active_reminder')
                self.calendar_event_ids.append(event_id)
            else:
                event_id = self.cal.calevent_create(date_to_mark, reminder['event'] + " (Selesai)", 'completed_reminder')
                self.calendar_event_ids.append(event_id)
        
        if ctk.get_appearance_mode() == "Dark":
            active_color = "#37FFAF"
            completed_color = "gray"
        else:
            active_color = "#4CAF50"
            completed_color = "lightgray"

        self.cal.tag_config('active_reminder', background=active_color, foreground="white")
        self.cal.tag_config('completed_reminder', background=completed_color, foreground="white")


    def show_reminders_for_selected_date(self, event=None):
        for widget in self.selected_date_reminders_frame.winfo_children():
            widget.destroy()

        selected_date_str = self.cal.get_date()
        selected_date = datetime.strptime(selected_date_str, '%d/%m/%Y').date()

        reminders_on_this_date = []
        for reminder in self.scheduled_reminders:
            if reminder['datetime'].date() == selected_date:
                reminders_on_this_date.append(reminder)
        
        reminders_on_this_date.sort(key=lambda x: x['datetime'])

        if not reminders_on_this_date:
            ctk.CTkLabel(self.selected_date_reminders_frame, text=f"Tidak ada jadwal pada {selected_date.strftime('%d %B %Y')}.", text_color="gray").pack(pady=5)
        else:
            for reminder in reminders_on_this_date:
                status = "(Selesai)" if reminder['notified'] else "(Akan Datang)"
                time_color = "gray" if reminder.get('notified') else "white" if ctk.get_appearance_mode() == "Dark" else "black"
                
                repeat_info = ""
                if reminder['repeat_type'] == 'yearly':
                    repeat_info = "(Setiap Tahun)"
                    if reminder['repeat_interval'] > 1:
                        repeat_info = f"(Setiap {reminder['repeat_interval']} Tahun)"
                elif reminder['repeat_type'] == 'monthly_interval':
                    repeat_info = f"(Setiap {reminder['repeat_interval']} Bulan)"

                # Menggunakan format_timezone_display di sini
                tz_display = self.format_timezone_display(reminder['datetime'])
                if tz_display:
                    reminder_time_str = reminder['datetime'].strftime(f'%H:%M {tz_display}')
                else:
                    reminder_time_str = reminder['datetime'].strftime('%H:%M')

                reminder_text = f"{reminder_time_str} - {reminder['event']} {repeat_info} {status}"
                ctk.CTkLabel(self.selected_date_reminders_frame, text=reminder_text, anchor="w", justify="left", font=("Arial", 11), text_color=time_color).pack(fill="x", padx=5, pady=1)


    def check_reminders_loop(self):
        now_local = datetime.now(LOCAL_TIMEZONE)
        reminders_updated = False

        reminders_to_process = self.scheduled_reminders[:]

        def add_months(sourcedate, months):
            month = sourcedate.month + months
            year = sourcedate.year + (month - 1) // 12
            month = (month - 1) % 12 + 1
            day = min(sourcedate.day, (datetime(year, month + 1, 1).date() - timedelta(days=1)).day if month < 12 else 31)
            return sourcedate.replace(year=year, month=month, day=day, tzinfo=sourcedate.tzinfo) 

        for i, reminder in enumerate(reminders_to_process):
            if now_local >= reminder['datetime'] and not reminder['notified']:
                notification.notify(
                    title="Pengingat Anda!",
                    message=f"Waktunya: {reminder['event']}",
                    app_name="AI Pengingat Pribadi",
                    timeout=10
                )
                reminders_updated = True

                if reminder['repeat_type'] == 'none':
                    original_index = self.scheduled_reminders.index(reminder)
                    self.scheduled_reminders[original_index]['notified'] = True
                else:
                    original_index = self.scheduled_reminders.index(reminder)
                    
                    # Debugging prints
                    print(f"\n--- Memproses Pengingat Berulang ---")
                    print(f"Event: {reminder['event']}")
                    print(f"Waktu Pemicu Saat Ini (reminder['datetime']): {reminder['datetime']}")
                    print(f"Waktu Sistem Saat Ini (now_local): {now_local}")
                    print(f"Tipe Pengulangan: {reminder['repeat_type']}")
                    print(f"Interval Pengulangan: {reminder['repeat_interval']}")

                    next_datetime = reminder['datetime']
                    
                    if reminder['repeat_type'] == 'yearly':
                        next_datetime = next_datetime.replace(year=next_datetime.year + reminder['repeat_interval'], tzinfo=next_datetime.tzinfo) 
                        print(f"Setelah perhitungan tahunan (pass pertama): {next_datetime}")
                    elif reminder['repeat_type'] == 'monthly_interval':
                        next_datetime = add_months(next_datetime, reminder['repeat_interval'])
                        print(f"Setelah perhitungan bulanan (pass pertama): {next_datetime}")
                        
                    loop_count = 0
                    while next_datetime <= now_local:
                        loop_count += 1
                        print(f"  Di dalam loop pengejaran (iterasi {loop_count}). next_datetime: {next_datetime}, now_local: {now_local}")
                        if reminder['repeat_type'] == 'yearly':
                            next_datetime = next_datetime.replace(year=next_datetime.year + reminder['repeat_interval'], tzinfo=next_datetime.tzinfo) 
                        elif reminder['repeat_type'] == 'monthly_interval':
                            next_datetime = add_months(next_datetime, reminder['repeat_interval'])
                        print(f"  next_datetime setelah maju di loop: {next_datetime}")
                                
                    self.scheduled_reminders[original_index]['datetime'] = next_datetime
                    self.scheduled_reminders[original_index]['notified'] = False
                    print(f"Waktu terjadwal berikutnya untuk '{reminder['event']}': {next_datetime}")
                    print(f"--- Selesai Memproses Pengingat Berulang ---\n")

        if reminders_updated:
            self.scheduled_reminders.sort(key=lambda x: x['datetime'])
            self.update_reminder_list()
            self.update_calendar_events()
            selected_date_str = self.cal.get_date()
            selected_date = datetime.strptime(selected_date_str, '%d/%m/%Y').date()
            if any(r['datetime'].date() == selected_date for r in self.scheduled_reminders):
                self.show_reminders_for_selected_date()

        self.master.after(1000, self.check_reminders_loop)

if __name__ == "__main__":
    root = ctk.CTk()
    app = ReminderApp(root)
    root.mainloop()