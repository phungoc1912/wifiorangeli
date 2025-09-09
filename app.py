import subprocess
import time
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# --- TEMPLATES HTML ---
# Sử dụng template string để giữ mọi thứ trong một file.
# CSS được nhúng trực tiếp để giao diện gọn gàng và tương thích với di động.

LAYOUT_TEMPLATE = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trình quản lý WiFi - Orange Pi</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
               background-color: #f0f2f5; color: #333; margin: 0; padding: 20px;
               display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .container { background-color: #fff; padding: 30px; border-radius: 10px;
                     box-shadow: 0 4px 12px rgba(0,0,0,0.1); width: 100%; max-width: 500px; }
        h1 { color: #ff6600; text-align: center; }
        .status { background-color: #e7f3ff; border-left: 5px solid #007bff; padding: 15px;
                  margin-bottom: 20px; border-radius: 5px; }
        .status-error { background-color: #ffebee; border-left: 5px solid #f44336; }
        label { font-weight: bold; margin-top: 15px; display: block; }
        select, input[type="password"], input[type="submit"] {
            width: 100%; padding: 12px; margin-top: 5px; border: 1px solid #ccc;
            border-radius: 5px; box-sizing: border-box; font-size: 16px; }
        input[type="submit"] { background-color: #ff6600; color: white; font-weight: bold;
                               border: none; cursor: pointer; transition: background-color 0.3s; }
        input[type="submit"]:hover { background-color: #e65c00; }
        .wifi-list { list-style-type: none; padding: 0; }
        .wifi-list li { padding: 10px; border-bottom: 1px solid #eee; cursor: pointer; }
        .wifi-list li:hover { background-color: #f9f9f9; }
        .footer { text-align: center; margin-top: 20px; font-size: 12px; color: #888; }
        .loader { margin: 20px auto; border: 5px solid #f3f3f3; border-top: 5px solid #ff6600;
                  border-radius: 50%; width: 50px; height: 50px; animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Trình quản lý WiFi</h1>
        {% block content %}{% endblock %}
        <div class="footer">Orange Pi Control Panel</div>
    </div>
</body>
</html>
"""

MAIN_PAGE_TEMPLATE = """
{% extends "layout" %}
{% block content %}
    {% if status.ssid %}
    <div class="status">
        <p><strong>Trạng thái:</strong> Đã kết nối</p>
        <p><strong>Mạng:</strong> {{ status.ssid }}</p>
        <p><strong>Địa chỉ IP:</strong> {{ status.ip }}</p>
        <p><small>Truy cập tại: <a href="http://orangepi.local">http://orangepi.local</a></small></p>
    </div>
    {% else %}
    <div class="status status-error">
        <p><strong>Trạng thái:</strong> Chưa kết nối. Vui lòng chọn một mạng để cấu hình.</p>
    </div>
    {% endif %}

    <form action="/connect" method="post">
        <label for="ssid">Chọn một mạng WiFi:</label>
        <select id="ssid" name="ssid" required>
            <option value="">-- Đang quét... --</option>
            {% for network in networks %}
            <option value="{{ network }}">{{ network }}</option>
            {% endfor %}
        </select>
        <label for="password">Mật khẩu:</label>
        <input type="password" id="password" name="password">
        <br><br>
        <input type="submit" value="Kết nối">
    </form>
{% endblock %}
"""

CONNECTING_TEMPLATE = """
{% extends "layout" %}
{% block content %}
    <h2 style="text-align:center;">Đang kết nối tới mạng "{{ ssid }}"...</h2>
    <p style="text-align:center;">Vui lòng đợi khoảng 15-20 giây. Trang sẽ tự động kiểm tra trạng thái.</p>
    <div class="loader"></div>
    <meta http-equiv="refresh" content="15;url=/status">
{% endblock %}
"""

STATUS_TEMPLATE = """
{% extends "layout" %}
{% block content %}
    {% if success %}
    <div class="status">
        <h2>✅ Kết nối thành công!</h2>
        <p>Orange Pi của bạn đã được kết nối vào mạng <strong>{{ ssid }}</strong>.</p>
        <p>Địa chỉ IP mới là: <strong>{{ ip }}</strong></p>
        <p>Bạn có thể cần kết nối lại thiết bị của mình vào cùng mạng WiFi và truy cập vào địa chỉ IP mới hoặc <a href="http://orangepi.local">http://orangepi.local</a>.</p>
    </div>
    {% else %}
    <div class="status status-error">
        <h2>❌ Kết nối thất bại</h2>
        <p>Không thể kết nối vào mạng <strong>{{ ssid }}</strong>. Vui lòng kiểm tra lại mật khẩu và thử lại.</p>
        <a href="/">Quay lại trang chính</a>
    </div>
    {% endif %}
{% endblock %}
"""

# --- CÁC HÀM HỖ TRỢ ---

def get_current_connection():
    """Lấy thông tin kết nối WiFi hiện tại (SSID và IP)."""
    try:
        ssid = subprocess.check_output(['iwgetid', '-r'], text=True).strip()
        ip_raw = subprocess.check_output(['hostname', '-I'], text=True).strip()
        ip = ip_raw.split()[0] # Lấy IP đầu tiên nếu có nhiều
        return {"ssid": ssid, "ip": ip}
    except subprocess.CalledProcessError:
        return {"ssid": None, "ip": None}

def scan_wifi_networks():
    """Quét và trả về danh sách các SSID duy nhất."""
    try:
        # Yêu cầu nmcli quét lại
        subprocess.run(['nmcli', 'dev', 'wifi', 'rescan'], timeout=10)
        time.sleep(3) # Đợi một chút để quá trình quét hoàn tất
        
        # Lấy danh sách mạng
        result = subprocess.check_output(['nmcli', '-f', 'SSID', 'dev', 'wifi', 'list', '--rescan', 'no'], text=True)
        lines = result.strip().split('\n')[1:] # Bỏ dòng tiêu đề
        ssids = {line.strip() for line in lines if line.strip() and line.strip() != '--'}
        return sorted(list(ssids))
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return []

# --- CÁC ROUTE CỦA FLASK ---

@app.route("/")
def index():
    """Trang chính: Hiển thị trạng thái và danh sách WiFi."""
    status = get_current_connection()
    networks = scan_wifi_networks()
    return render_template_string(
        MAIN_PAGE_TEMPLATE,
        status=status,
        networks=networks,
        layout=LAYOUT_TEMPLATE
    )

@app.route("/connect", methods=["POST"])
def connect():
    """Xử lý yêu cầu kết nối WiFi."""
    ssid = request.form.get("ssid")
    password = request.form.get("password", "") # Mật khẩu có thể rỗng

    if not ssid:
        return "Lỗi: Tên WiFi (SSID) không được cung cấp.", 400

    # Lưu lại ssid để hiển thị trên trang trạng thái
    global last_attempted_ssid
    last_attempted_ssid = ssid

    try:
        # Sử dụng nmcli để kết nối. Lệnh này sẽ tự động tạo và quản lý connection profile.
        command = ['nmcli', 'dev', 'wifi', 'connect', ssid]
        if password:
            command.extend(['password', password])
        
        # Chạy lệnh với timeout
        subprocess.run(command, check=True, timeout=30)
        
        # Nếu lệnh chạy xong mà không có lỗi, nmcli thường đã kết nối thành công.
        # Chuyển hướng ngay đến trang trạng thái để xác nhận.
        return redirect(url_for('status'))

    except subprocess.TimeoutExpired:
        # Nếu timeout, rất có thể kết nối thất bại (sai pass, sóng yếu)
        return redirect(url_for('status'))
    except subprocess.CalledProcessError as e:
        # Nếu nmcli trả về lỗi, cũng là thất bại
        print(f"Lỗi khi kết nối nmcli: {e}")
        return redirect(url_for('status'))

@app.route("/status")
def status():
    """Trang kiểm tra trạng thái sau khi kết nối."""
    global last_attempted_ssid
    ssid_to_check = last_attempted_ssid
    
    # Đợi một chút để network interface nhận IP mới
    time.sleep(5)
    
    current = get_current_connection()
    
    if current["ssid"] == ssid_to_check:
        return render_template_string(
            STATUS_TEMPLATE,
            success=True,
            ssid=current["ssid"],
            ip=current["ip"],
            layout=LAYOUT_TEMPLATE
        )
    else:
        return render_template_string(
            STATUS_TEMPLATE,
            success=False,
            ssid=ssid_to_check,
            layout=LAYOUT_TEMPLATE
        )

# --- KHỞI CHẠY APP ---
# Biến global để lưu lại ssid vừa thử kết nối
last_attempted_ssid = ""

# Gán template layout cho các template con
@app.context_processor
def inject_layout():
    return dict(layout=LAYOUT_TEMPLATE)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)

