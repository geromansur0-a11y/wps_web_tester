# WPS WPA Tester Web Dashboard

Aplikasi berbasis web untuk melakukan pengujian keamanan jaringan WPS menggunakan 
Reaver, Wash, dan PixieWPS melalui antarmuka browser yang interaktif.

## Fitur
- 📡 **Live Scanning**: Scan jaringan WPS secara real-time.
- ⚡ **Pixie-Dust Attack**: Integrasi otomatis dengan reaver & pixiewps.
- 🖥️ **Web Terminal**: Output log terminal langsung di browser via WebSockets.
- 💾 **SQLite Database**: Menyimpan otomatis password yang berhasil ditemukan.

## Persyaratan
- Perangkat Android (Root) dengan Termux atau Linux (Kali/Ubuntu).
- Kartu Wi-Fi yang mendukung **Monitor Mode**.
- Tools terinstal: `reaver`, `pixiewps`, `aircrack-ng`.

## Cara Instalasi
1. Clone repo ini:
   ```bash
   git clone [https://github.com/username/WPS-Web-Tester.git](https://github.com/username/WPS-Web-Tester.git)
   cd WPS-Web-Tester
