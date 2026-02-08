# AutoRes Pro

Tự động đổi độ phân giải màn hình khi chạy game và khôi phục lại khi thoát.

Ứng dụng chạy nền với tray icon, có giao diện debug và quản lý game.

---

## Tính năng

- Tự động phát hiện game khởi động bằng WMI
- Tự khôi phục độ phân giải khi game tắt
- Tray icon đổi trạng thái realtime
- Lưu cấu hình vào file config.json
- Hỗ trợ nhiều game
- Giao diện debug log realtime
- Cho phép chỉnh độ phân giải theo game
- Lưu và khôi phục độ phân giải hiện tại
- Chạy nền, không cần console

Cơ chế hoạt động:

- Detect start: WMI event (nhẹ CPU)
- Detect exit: kiểm tra process bằng psutil
- Đổi độ phân giải: win32 API / nircmd (embedded)

---

## Yêu cầu (nếu chạy từ source)

Python 3.10+

Cài thư viện:

```bash
pip install pystray pillow pywin32 wmi psutil
````

---

## Chạy từ source

```bash
python auto_res_pro_tray_wmi.py
```

---

## Build file EXE (Nuitka)

Ví dụ lệnh build:

```bash
python -m nuitka auto_res_pro_tray_wmi.py ^
--standalone ^
--onefile ^
--windows-disable-console ^
--enable-plugin=tk-inter ^
--include-package=win32com ^
--include-package=pythoncom ^
--include-package=pywintypes ^
--include-package=wmi ^
--include-package=psutil
```

File exe sẽ nằm trong thư mục:

```
dist/
```

---

## Cấu hình

File:

```
config.json
```

Ví dụ:

```json
{
  "games": [
    {
      "name": "Delta Force",
      "process": "DeltaForceClient-Win64-Shipping.exe"
    }
  ],
  "current_game": 0,
  "game_resolution": [1440, 1080, 32, 60],
  "last_user_resolution": null
}
```

---

## Cách sử dụng

1. Chạy chương trình
2. Icon xuất hiện ở system tray
3. Click chuột phải:

   * Chọn game
   * Chỉnh độ phân giải
   * Xem debug log

Khi game chạy:

* Đổi độ phân giải tự động

Khi game tắt:

* Khôi phục độ phân giải ban đầu

---

## Lưu ý

* Một số game có anti-cheat có thể không cho đổi resolution ngoài game.
* Nên chạy bằng quyền Administrator nếu đổi độ phân giải thất bại.

---

## Cấu trúc chính

* Hybrid monitor (WMI + psutil)
* Tray UI (pystray)
* Debug window (tkinter)
* Config system (JSON)

---

## License

Personal use.

