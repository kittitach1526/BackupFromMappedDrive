import os
import shutil
import filecmp
from datetime import datetime, timedelta
import schedule
import time

import configparser
import threading
import tkinter as tk
from concurrent.futures import ThreadPoolExecutor, as_completed

config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")

mapped_drives_str = config.get("BackupSettings", "mapped_drives", fallback=r"Y:\\")
mapped_drives = [d.strip() for d in mapped_drives_str.split(",") if d.strip()]

destination_bases_str = config.get("BackupSettings", "destination_base", fallback=r"C:\Backup_AllMappedDrives")
destination_bases = [d.strip() for d in destination_bases_str.split(",") if d.strip()]

log_file = config.get("BackupSettings", "log_file", fallback=r"C:\Backup_AllMappedDrives\backup_log.txt")

MAX_DEPTH = config.getint("BackupSettings", "max_depth", fallback=50)
MAX_BACKUP_AGE_DAYS = config.getint("BackupSettings", "max_backup_age_days", fallback=7)
MAX_THREADS = config.getint("BackupSettings", "max_threads", fallback=8)

print("Mapped Drives:", mapped_drives)
print("Destination Bases:", destination_bases)
print("Log File:", log_file)
print("Max Depth:", MAX_DEPTH)
print("Max Backup Age Days:", MAX_BACKUP_AGE_DAYS)
print("Max Threads:", MAX_THREADS)

file_copy_executor = ThreadPoolExecutor(max_workers=MAX_THREADS)


def show_notification(title, message, duration=1800):
    def run():
        root = tk.Tk()
        root.title(title)
        root.geometry("400x150")
        root.attributes("-topmost", True)
        root.resizable(False, False)

        label = tk.Label(root, text=message, font=("Arial", 12), wraplength=380)
        label.pack(expand=True, fill="both", padx=10, pady=10)

        def close_window():
            root.destroy()

        root.after(duration * 1000, close_window)
        root.mainloop()

    threading.Thread(target=run, daemon=True).start()


def write_log(message):
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = f"[{timestamp}] {message}\n"
    print(log_line, end="")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_line)


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
                write_log(f"[ERROR] ไม่สามารถลบ backup เก่า {item_path}: {e}")


def copy_file_task(s_path, d_path):
    try:
        os.makedirs(os.path.dirname(d_path), exist_ok=True)
        if not os.path.exists(d_path) or not filecmp.cmp(s_path, d_path, shallow=False):
            shutil.copy2(s_path, d_path)
            write_log(f"Copied: {s_path} → {d_path}")
    except Exception as e:
        write_log(f"[ERROR] คัดลอกไฟล์ล้มเหลว {s_path} → {d_path}: {e}")


def sync_folders(source, destination, depth=0):
    if depth > MAX_DEPTH:
        write_log(f"[WARN] เกินความลึก {MAX_DEPTH} ที่: {source}")
        return

    tasks = []

    try:
        if not os.path.exists(destination):
            os.makedirs(destination)

        for item in os.listdir(source):
            s_path = os.path.join(source, item)
            d_path = os.path.join(destination, item)

            if os.path.islink(s_path):
                write_log(f"[SKIP] ละเว้น symlink: {s_path}")
                continue

            if os.path.isdir(s_path):
                sync_folders(s_path, d_path, depth + 1)
            else:
                task = file_copy_executor.submit(copy_file_task, s_path, d_path)
                tasks.append(task)

        for task in as_completed(tasks):
            pass
    except Exception as e:
        write_log(f"[ERROR] เกิดข้อผิดพลาดที่ {source}: {e}")


def backup_drive_to_destination(source_dir, destination_base):
    drive_letter = source_dir.strip("\\").replace(":", "")
    time_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    destination_dir = os.path.join(destination_base, f"{drive_letter}_{time_str}")
    write_log(f"🔁 เริ่มสำรองข้อมูลจาก {source_dir} → {destination_dir}")

    if os.path.exists(source_dir):
        sync_folders(source_dir, destination_dir)
        write_log(f"✅ เสร็จสิ้นสำรอง {source_dir} ที่ {destination_dir} เวลา {datetime.now()}")
        msg = f"✅ เสร็จสิ้นสำรอง {source_dir} ที่ {destination_dir} เวลา {datetime.now()}"
        show_notification("Backup Completed", msg)
    else:
        write_log(f"❌ ไม่สามารถเข้าถึงไดรฟ์ {source_dir} หรือไม่ได้เชื่อมต่อ")
        msg = f"❌ ไม่สามารถเข้าถึงไดรฟ์ {source_dir} หรือไม่ได้เชื่อมต่อ"
        show_notification("Backup Error", msg)


def backup_drive(source_dir):
    cleanup_old_backups(destination_bases)

    with ThreadPoolExecutor(max_workers=len(destination_bases)) as dest_executor:
        futures = []
        for dest_base in destination_bases:
            futures.append(dest_executor.submit(backup_drive_to_destination, source_dir, dest_base))

        for f in as_completed(futures):
            pass


def backup_all():
    write_log(f"🕒 เริ่มกระบวนการสำรองข้อมูลทั้งหมด")

    with ThreadPoolExecutor(max_workers=len(mapped_drives)) as drive_executor:
        futures = []
        for drive in mapped_drives:
            futures.append(drive_executor.submit(backup_drive, drive))

        for f in as_completed(futures):
            pass

    write_log(f"🕒 กระบวนการสำรองข้อมูลทั้งหมดเสร็จสิ้น\n")


schedule.every().day.at("01:00").do(backup_all)

if __name__ == "__main__":
    write_log("🚀 โปรแกรมสำรองข้อมูลทำงานอยู่... (รอเวลา)")
    backup_all()
    while True:
        schedule.run_pending()
        time.sleep(60)
