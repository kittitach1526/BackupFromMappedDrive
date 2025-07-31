import os
import shutil
from datetime import datetime, timedelta
import schedule
import time
import configparser
import threading
import tkinter as tk
import concurrent.futures
import queue
import subprocess
import sys

# --------------------- CONFIG ---------------------
config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

mapped_drives_str = config.get("BackupSettings", "mapped_drives", fallback=r"Y:\\")
mapped_drives = [d.strip() for d in mapped_drives_str.split(",") if d.strip()]

destination_bases_str = config.get("BackupSettings", "destination_base", fallback=r"C:\Backup_AllMappedDrives")
destination_bases = [d.strip() for d in destination_bases_str.split(",") if d.strip()]

log_file = config.get("BackupSettings", "log_file", fallback=r"C:\Backup_AllMappedDrives\backup_log.txt")

MAX_BACKUP_AGE_DAYS = config.getint("BackupSettings", "max_backup_age_days", fallback=7)
EXCLUDE_EXTENSIONS = [".tmp", ".log", ".bak", ".db", ".lnk", ".~"]

# --------------------- ASYNC LOGGING ---------------------
log_queue = queue.Queue()

def async_logger():
    while True:
        msg = log_queue.get()
        if msg == "__EXIT__":
            break
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {msg}\n"
        print(log_line, end="")
        try:
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception as e:
            print(f"[LOG ERROR] {e}")

log_thread = threading.Thread(target=async_logger, daemon=True)
log_thread.start()

def write_log(msg):
    log_queue.put(msg)

# --------------------- GUI NOTIFY ---------------------
def show_notification(title, message, duration=30):
    def run():
        root = tk.Tk()
        root.title(title)
        root.geometry("400x150")
        root.attributes("-topmost", True)
        root.resizable(False, False)
        label = tk.Label(root, text=message, font=("Arial", 12), wraplength=380)
        label.pack(expand=True, fill="both", padx=10, pady=10)
        root.after(duration * 1000, root.destroy)
        root.mainloop()
    threading.Thread(target=run, daemon=True).start()

# --------------------- CLEANUP ---------------------
def cleanup_old_backups(base_folders, max_age_days=MAX_BACKUP_AGE_DAYS):
    now = datetime.now()
    cutoff = now - timedelta(days=max_age_days)
    for base_folder in base_folders:
        if not os.path.exists(base_folder):
            continue
        for item in os.listdir(base_folder):
            item_path = os.path.join(base_folder, item)
            try:
                if os.path.isdir(item_path):
                    mod_time = datetime.fromtimestamp(os.path.getmtime(item_path))
                    if mod_time < cutoff:
                        shutil.rmtree(item_path)
                        write_log(f"Deleted old backup: {item_path}")
            except Exception as e:
                write_log(f"[ERROR] ลบ backup เก่าไม่ได้: {item_path} → {e}")

# --------------------- BACKUP ---------------------
def robocopy_backup(source_dir, destination_dir):
    try:
        os.makedirs(destination_dir, exist_ok=True)
        cmd = [
            "robocopy",
            source_dir,
            destination_dir,
            "/MIR",        # mirror
            "/FFT",        # loose timestamp
            "/Z",          # restartable mode
            # อยากเห็นรายละเอียดไฟล์ก็ไม่ต้องใส่ /NP, /NDL, /NJH, /NJS
        ]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            line = line.strip()
            if line:
                write_log(f"[RoboCopy] {line}")
        process.wait()
    except Exception as e:
        write_log(f"[ERROR] robocopy failed ({source_dir} → {destination_dir}): {e}")

def backup_drive(source_dir):
    drive_letter = source_dir.strip("\\").replace(":", "")
    time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    for destination_base in destination_bases:
        destination_dir = os.path.join(destination_base, f"{drive_letter}_{time_str}")
        write_log(f"🚀 เริ่มสำรอง {source_dir} → {destination_dir}")
        if os.path.exists(source_dir):
            robocopy_backup(source_dir, destination_dir)
            write_log(f"✅ เสร็จสิ้นสำรอง {source_dir} ที่ {destination_dir}")
            show_notification("Backup Completed", f"✅ เสร็จสิ้นสำรอง {source_dir} แล้ว")
        else:
            write_log(f"❌ ไม่พบหรือเข้าถึงไดรฟ์ {source_dir}")
            show_notification("Backup Error", f"❌ ไม่พบไดรฟ์ {source_dir}")

def backup_all():
    write_log("📦 เริ่ม backup ทั้งหมด")
    cleanup_old_backups(destination_bases)
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(mapped_drives))) as executor:
        futures = [executor.submit(backup_drive, drive) for drive in mapped_drives]
        for f in concurrent.futures.as_completed(futures):
            try:
                f.result()
            except Exception as e:
                write_log(f"[ERROR] Backup thread crash: {e}")
    write_log("📦 เสร็จสิ้น backup ทั้งหมด\n")

# --------------------- SCHEDULE ---------------------
schedule.every().day.at("01:00").do(backup_all)


# ANSI รหัสสีรุ้ง
rainbow_colors = [
    '\033[91m',  # Red
    '\033[93m',  # Yellow
    '\033[92m',  # Green
    '\033[96m',  # Cyan
    '\033[94m',  # Blue
    '\033[95m',  # Magenta
]

reset = '\033[0m'

ascii_art = """
███████╗██████╗ ██╗  ██╗██╗  ██╗   ██████╗ ███████╗██╗   ██╗
██╔════╝██╔══██╗██║  ██║╚██╗██╔╝   ██╔══██╗██╔════╝██║   ██║
███████╗██████╔╝███████║ ╚███╔╝    ██║  ██║█████╗  ██║   ██║
╚════██║██╔═══╝ ██╔══██║ ██╔██╗    ██║  ██║██╔══╝  ╚██╗ ██╔╝
███████║██║     ██║  ██║██╔╝ ██╗██╗██████╔╝███████╗ ╚████╔╝ 
╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝  ╚═══╝  
"""

def print_rainbow(text):
    color_index = 0
    for char in text:
        if char != '\n' and char != ' ':
            sys.stdout.write(rainbow_colors[color_index % len(rainbow_colors)] + char + reset)
            color_index += 1
        else:
            sys.stdout.write(char)
    sys.stdout.flush()

if __name__ == "__main__":
    
    print_rainbow(ascii_art)

    write_log("🟢 BACKUP V2.3 START")
    backup_all()
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        write_log("🛑 หยุดโปรแกรมด้วยมือ")
    finally:
        log_queue.put("__EXIT__")
        log_thread.join()
