#!/bin/bash

# Warna untuk output
G='\033[0;32m'
R='\033[0;31m'
Y='\033[1;33m'
B='\033[0;34m'
NC='\033[0m'

echo -e "${B}===========================================${NC}"
echo -e "${G}    WPS Web Tester Auto-Installer          ${NC}"
echo -e "${B}===========================================${NC}"

# 1. Cek apakah ini di Termux atau Linux standar
if [ -d "/data/data/com.termux/files/usr/bin" ]; then
    IS_TERMUX=true
    echo -e "${Y}[*] Mendeteksi lingkungan: Termux${NC}"
else
    IS_TERMUX=false
    echo -e "${Y}[*] Mendeteksi lingkungan: Linux Standar${NC}"
fi

# 2. Update sistem dan install tools dasar
echo -e "${Y}[*] Mengupdate repository dan menginstall tools...${NC}"
if [ "$IS_TERMUX" = true ]; then
    pkg update -y && pkg upgrade -y
    pkg install root-repo -y
    pkg install python tsu aircrack-ng reaver pixiewps sqlite -y
else
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip aircrack-ng reaver pixiewps sqlite3
fi

# 3. Install dependensi Python
echo -e "${Y}[*] Menginstall library Python (Flask, SocketIO)...${NC}"
if [ "$IS_TERMUX" = true ]; then
    pip install flask flask-socketio eventlet
else
    pip3 install flask flask-socketio eventlet
fi

# 4. Membuat shortcut untuk menjalankan aplikasi
echo -e "${Y}[*] Membuat file executable 'run.sh'...${NC}"
cat <<EOF > run.sh
#!/bin/bash
if [ -d "/data/data/com.termux/files/usr/bin" ]; then
    sudo python app.py
else
    sudo python3 app.py
fi
EOF
chmod +x run.sh

# 5. Selesai
echo -e "${B}-------------------------------------------${NC}"
echo -e "${G}[V] Instalasi Selesai!${NC}"
echo -e "${Y}Cara menjalankan:${NC}"
echo -e " 1. Aktifkan monitor mode: ${G}sudo airmon-ng start wlan0${NC}"
echo -e " 2. Jalankan server:       ${G}./run.sh${NC}"
echo -e " 3. Buka di browser:       ${G}http://localhost:5000${NC}"
echo -e "${B}-------------------------------------------${NC}"
