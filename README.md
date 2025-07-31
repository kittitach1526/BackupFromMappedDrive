# 🗂️ Auto Backup Tool for Mapped Drives

โปรแกรม Python สำหรับสำรองข้อมูลจาก Mapped Drive (หรือ UNC path) ไปยังปลายทางที่กำหนด โดยรองรับการทำงานแบบอัตโนมัติทุกวัน พร้อมระบบแสดงแจ้งเตือนผ่านหน้าต่าง GUI และระบบจัดการ log

## ✅ คุณสมบัติ

- รองรับการสำรองข้อมูลจากหลายไดรฟ์พร้อมกัน
- ลบ backup เก่าตามจำนวนวันที่กำหนด (default: 7 วัน)
- แจ้งเตือนผ่าน GUI (Tkinter) เมื่อสำรองเสร็จหรือเกิดข้อผิดพลาด
- ตั้งเวลาสำรองข้อมูลอัตโนมัติไว้ที่ 1:00 ของทุกวัน
- เขียน log การทำงานลงไฟล์

---

## 🛠️ การตั้งค่า (config.ini)

สร้างไฟล์ชื่อ `config.ini` ในโฟลเดอร์เดียวกับ `main.py` และกำหนดค่าต่อไปนี้:

```ini
[BackupSettings]
mapped_drives = Y:/, F:/, G:/, H:/, I:/, J:/, K:/, L:/, N:/, O:/, P:/, Q:/, R:/, S:/, T:/, U:/, V:/, W:/, X:/, Z:/
destination_base = D:/test_backup, E:/test_backup
log_file = C:/Users/BACKUP-MACHINE/Desktop/log_backup.txt
max_depth = 30
max_backup_age_days = 7
max_threads = 12


