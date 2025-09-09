import subprocess
import re
from flask import Flask, render_template_string, request, redirect, jsonify

app = Flask(__name__)

# --- TEMPLATES HTML ---
# Mỗi template giờ là một file HTML hoàn chỉnh

SETUP_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cài đặt WiFi - Orange Pi</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f4f9; color: #333; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .container { background-color: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 90%; max-width: 400px; }
        h1 { color: #4a4a4a; text-align: center; }
        form div { margin-bottom: 1rem; }
        label { display: block; margin-bottom: 0.5rem; font-weight: bold; }
        select, input[type="password"], input[type="text"] { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        .btn { display: block; width: 100%; padding: 1rem; border: none; border-radius: 4px; background-color: #5a67d8; color: white; font-size: 1rem; cursor: pointer; text-align: center; text-decoration: none; }
        .btn:hover { background-color: #434190; }
        .status { margin-top: 1rem; padding: 1rem; border-radius: 4px; text-align: center; word-wrap: break-word; }
        .status.success { background-color: #e6fffa; border: 1px solid #38c172; color: #1f9d55; }
        .status.error { background-color: #fff5f5; border: 1px solid #e53e3e; color: #c53030; }
        .hidden { display: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📶 Cài đặt WiFi</h1>
        <div class="status success">
            <strong>Trạng thái:</strong> {{ current_ssid or 'Chưa kết nối' }}<br>
            <strong>Các địa chỉ IP:</strong> {{ current_ips or 'N/A' }}
        </div>
        <hr style="margin: 1.5rem 0; border: 1px solid #eee;">
        <form action="/connect" method="post">
            <div>
                <label for="ssid">Chọn mạng WiFi:</label>
                <select id="ssid" name="ssid" required>
                    <option value="">-- Đang quét... --</option>
                    {% for network in networks %}
                    <option value="{{ network }}">{{ network }}</option>
                    {% endfor %}
                </select>
            </div>
            <div>
                <label for="password">Mật khẩu:</label>
                <input type="password" id="password" name="password">
            </div>
            <button type="submit" class="btn">Kết nối</button>
        </form>
    </div>
</body>
</html>
"""

CONNECTING_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đang kết nối...</title>
    <meta http-equiv="refresh" content="10;url=/">
    <style>
        body { font-family: sans-serif; background-color: #f4f4f9; color: #333; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; text-align: center; }
        .container { background-color: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .loader { border: 8px solid #f3f3f3; border-radius: 50%; border-top: 8px solid #5a67d8; width: 60px; height: 60px; animation: spin 2s linear infinite; margin: 0 auto 1rem; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="loader"></div>
        <h1>Đang thử kết nối vào mạng "{{ ssid }}"...</h1>
        <p>Vui lòng đợi trong giây lát. Trang sẽ tự động làm mới sau 10 giây.</p>
        <p>Nếu kết nối thành công, bạn có thể cần kết nối lại vào mạng WiFi chính và truy cập Orange Pi bằng địa chỉ IP mới.</p>
        <a href="/">Quay lại</a>
    </div>
</body>
</html>
"""

# --- LOGIC PYTHON ---

def run_command(command):
    """Hàm helper để chạy lệnh và trả về output."""
    try:
        result = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        return result.strip()
    except subprocess.CalledProcessError as e:
        print(f"Lỗi khi chạy lệnh '{command}': {e.output}")
        return None

def get_wifi_networks():
    """Quét các mạng WiFi bằng nmcli."""
    # nmcli có thể cần chạy lại vài lần để có kết quả
    run_command("nmcli dev wifi rescan")
    # Lấy các trường SSID, SIGNAL, SECURITY
    output = run_command("nmcli --terse --fields SSID,SIGNAL,SECURITY dev wifi list")
    if not output:
        return []
    
    seen_ssids = set()
    networks = []
    for line in output.split('\n'):
        parts = line.split(':')
        if len(parts) >= 1 and parts[0]:
            ssid = parts[0]
            if ssid not in seen_ssids:
                seen_ssids.add(ssid)
                networks.append(ssid)
    return sorted(list(networks))

def get_current_connection():
    """Lấy SSID và tất cả địa chỉ IP hiện tại."""
    ssid = run_command("iwgetid -r")
    # hostname -I sẽ trả về một chuỗi chứa tất cả các địa chỉ IP, cách nhau bởi dấu cách.
    ip_addresses = run_command("hostname -I")
    return ssid, ip_addresses

@app.route("/")
def index():
    networks = get_wifi_networks()
    current_ssid, current_ips = get_current_connection()
    return render_template_string(
        SETUP_TEMPLATE,
        networks=networks,
        current_ssid=current_ssid,
        current_ips=current_ips
    )

@app.route("/connect", methods=["POST"])
def connect():
    ssid = request.form.get("ssid")
    password = request.form.get("password", "") # Mật khẩu có thể trống

    if not ssid:
        return "Lỗi: Tên SSID không được cung cấp.", 400

    print(f"Thử kết nối vào SSID: {ssid}")
    
    # Lệnh nmcli để kết nối. Nếu không có mật khẩu, bỏ qua phần password.
    if password:
        command = f"nmcli dev wifi connect '{ssid}' password '{password}'"
    else:
        command = f"nmcli dev wifi connect '{ssid}'"

    connection_result = run_command(command)
    print(f"Kết quả kết nối: {connection_result}")

    return render_template_string(CONNECTING_TEMPLATE, ssid=ssid)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
