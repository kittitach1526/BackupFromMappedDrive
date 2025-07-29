# 🗂️ Auto Backup Tool for Mapped Drives

โปรแกรม Python สำหรับสำรองข้อมูลจาก Mapped Drive (หรือ UNC path) ไปยังปลายทางที่กำหนด โดยรองรับการทำงานแบบอัตโนมัติทุกวัน พร้อมระบบแสดงแจ้งเตือนผ่านหน้าต่าง GUI และระบบจัดการ log

## ✅ คุณสมบัติ

- รองรับการสำรองข้อมูลจากหลายไดรฟ์พร้อมกัน
- ลบ backup เก่าตามจำนวนวันที่กำหนด (default: 7 วัน)
- แจ้งเตือนผ่าน GUI (Tkinter) เมื่อสำรองเสร็จหรือเกิดข้อผิดพลาด
- ตั้งเวลาสำรองข้อมูลอัตโนมัติ (default: 01:00 ทุกวัน)
- เขียน log การทำงานลงไฟล์

---

## 🛠️ การตั้งค่า (config.ini)

สร้างไฟล์ชื่อ `config.ini` ในโฟลเดอร์เดียวกับ `main.py` และกำหนดค่าต่อไปนี้:

```ini
[BackupSettings]
mapped_drives = Y:\\, Z:\\                      ; ไดรฟ์ที่ต้องการสำรองข้อมูล
destination_base = C:\BackupDrive               ; โฟลเดอร์ปลายทาง
log_file = C:\BackupDrive\backup_log.txt        ; ไฟล์ log
max_depth = 50                                  ; ความลึกสูงสุดในการสำรอง
max_backup_age_days = 7                         ; ลบ backup เก่ากว่า n วัน
