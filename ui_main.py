import configparser
import customtkinter as ctk
from tkinter import messagebox, filedialog

CONFIG_PATH = "config.ini"

# โหลด config เดิม
config = configparser.ConfigParser()
config.read(CONFIG_PATH, encoding="utf-8")

if not config.has_section("BackupSettings"):
    config.add_section("BackupSettings")

def save_config(mapped_drives, destination_base, log_file, max_backup_age):
    config.set("BackupSettings", "mapped_drives", mapped_drives)
    config.set("BackupSettings", "destination_base", destination_base)
    config.set("BackupSettings", "log_file", log_file)
    # config.set("BackupSettings", "max_depth", str(max_depth))
    config.set("BackupSettings", "max_backup_age_days", str(max_backup_age))
    with open(CONFIG_PATH, "w", encoding="utf-8") as configfile:
        config.write(configfile)
    messagebox.showinfo("บันทึกสำเร็จ", "ตั้งค่าได้ถูกบันทึกลง config.ini แล้ว")

# ฟังก์ชันเปิด Folder dialog เพื่อเลือกโฟลเดอร์ และเพิ่มลงใน entry (แบบ list คั่นด้วย comma)
def add_folder_to_entry(entry_widget):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        current = entry_widget.get().strip()
        paths = [p.strip() for p in current.split(",") if p.strip()]
        if folder_selected not in paths:
            paths.append(folder_selected)
            entry_widget.delete(0, ctk.END)
            entry_widget.insert(0, ", ".join(paths))

# ฟังก์ชันเปิดไฟล์ dialog เพื่อเลือกไฟล์ log
def select_file(entry_widget):
    file_selected = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt"), ("All files","*.*")])
    if file_selected:
        entry_widget.delete(0, ctk.END)
        entry_widget.insert(0, file_selected)

# สร้างหน้าต่างหลัก
ctk.set_appearance_mode("System")  # โหมดแสงตามระบบ
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Backup Config")
app.geometry("600x450")

# Mapped Drives (แก้เป็น text input + ปุ่มเพิ่มโฟลเดอร์หลายไดรฟ์)
label_md = ctk.CTkLabel(app, text=r"Mapped Drives (คั่นด้วย , เช่น Y:\, Z:\):")
label_md.pack(padx=20, pady=(20, 5))

frame_md = ctk.CTkFrame(app)
frame_md.pack(padx=20, pady=5, fill="x")

entry_md = ctk.CTkEntry(frame_md)
entry_md.pack(side="left", fill="x", expand=True)

btn_add_md = ctk.CTkButton(frame_md, text="เพิ่มไดรฟ์", width=80, command=lambda: add_folder_to_entry(entry_md))
btn_add_md.pack(side="right", padx=5)

# Backup Destination Base Folder (แบบเดียวกับ mapped drives)
label_db = ctk.CTkLabel(app, text="Backup Destination Base Folder(s) (คั่นด้วย , ):")
label_db.pack(padx=20, pady=(20, 5))

frame_db = ctk.CTkFrame(app)
frame_db.pack(padx=20, pady=5, fill="x")

entry_db = ctk.CTkEntry(frame_db)
entry_db.pack(side="left", fill="x", expand=True)

btn_add_db = ctk.CTkButton(frame_db, text="เพิ่มโฟลเดอร์", width=120, command=lambda: add_folder_to_entry(entry_db))
btn_add_db.pack(side="right", padx=5)

# Log File Path
label_log = ctk.CTkLabel(app, text="Log File Path:")
label_log.pack(padx=20, pady=(20, 5))

frame_log = ctk.CTkFrame(app)
frame_log.pack(padx=20, pady=5, fill="x")

entry_log = ctk.CTkEntry(frame_log)
entry_log.pack(side="left", fill="x", expand=True)

btn_log = ctk.CTkButton(frame_log, text="เลือกไฟล์", width=120, command=lambda: select_file(entry_log))
btn_log.pack(side="right", padx=5)

# Max Backup Age (days)
label_age = ctk.CTkLabel(app, text="Max Backup Age (days):")
label_age.pack(padx=20, pady=(20, 5))

entry_age = ctk.CTkEntry(app, width=100)
entry_age.pack(padx=20)

# โหลดค่าเดิมลงกล่องข้อความ
entry_md.insert(0, config.get("BackupSettings", "mapped_drives", fallback="Y:\\"))
entry_db.insert(0, config.get("BackupSettings", "destination_base", fallback=r"C:\backup1, D:\backup2"))
entry_log.insert(0, config.get("BackupSettings", "log_file", fallback=r"C:\backup1\backup_log.txt"))
entry_age.insert(0, config.get("BackupSettings", "max_backup_age_days", fallback="7"))

def on_save():
    md = entry_md.get().strip()
    db = entry_db.get().strip()
    log = entry_log.get().strip()
    age = entry_age.get().strip()

    # ตรวจสอบค่าที่กรอก
    if not md or not db or not log or not age.isdigit():
        messagebox.showerror("ผิดพลาด", "กรุณากรอกข้อมูลให้ครบและถูกต้อง")
        return

    save_config(md, db, log, int(age))

btn_save = ctk.CTkButton(app, text="บันทึกการตั้งค่า", command=on_save)
btn_save.pack(pady=30)

app.mainloop()
