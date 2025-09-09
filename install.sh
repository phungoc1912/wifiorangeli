#!/bin/bash

# Dừng ngay lập tức nếu có lỗi
set -e

# --- CẤU HÌNH ---
# !!! THAY THẾ BẰNG THÔNG TIN GITHUB CỦA BẠN !!!
GIT_USERNAME="phungoc1912"
GIT_REPO="wifiorangeli"
# --- KẾT THÚC CẤU HÌNH ---

INSTALL_DIR="/opt/orangepi-wifi-manager"
GIT_URL="https://github.com/$GIT_USERNAME/$GIT_REPO.git"

echo ">>> Bắt đầu quá trình cài đặt Trình quản lý WiFi bằng Docker..."

# 0. Kiểm tra quyền root
if [ "$(id -u)" -ne 0 ]; then
  echo "Lỗi: Vui lòng chạy kịch bản này với quyền root (sudo)." >&2
  exit 1
fi

# 1. Cài đặt các gói phụ thuộc trên máy chủ
echo ">>> [1/5] Cài đặt các gói phụ thuộc (Docker, Git, Avahi)..."
apt-get update
# Cài đặt các gói cần thiết cho việc clone và chạy .local
apt-get install -y git avahi-daemon

# Cài Docker
if ! command -v docker &> /dev/null; then
    echo "    - Docker chưa được cài đặt. Đang tiến hành cài đặt..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
else
    echo "    - Docker đã được cài đặt."
fi

# Cài Docker Compose plugin
if ! command -v docker-compose &> /dev/null; then
    apt-get install -y docker-compose-plugin
else
    echo "    - Docker Compose đã được cài đặt."
fi

# 2. Kích hoạt dịch vụ Avahi
echo ">>> [2/5] Kích hoạt dịch vụ Avahi (cho .local domain)..."
systemctl enable avahi-daemon
systemctl restart avahi-daemon

# 3. Tải mã nguồn từ GitHub
echo ">>> [3/5] Tải mã nguồn từ $GIT_URL..."
# Xóa thư mục cũ nếu tồn tại
rm -rf $INSTALL_DIR
# Clone repository mới
git clone $GIT_URL $INSTALL_DIR

# 4. Build và khởi chạy container
echo ">>> [4/5] Build image và khởi chạy container..."
cd $INSTALL_DIR
docker compose up -d --build

# 5. Dọn dẹp (tùy chọn)
echo ">>> [5/5] Dọn dẹp các image không cần thiết..."
docker image prune -f

echo ""
echo "✅ HOÀN TẤT!"
echo "Ứng dụng Trình quản lý WiFi đã được triển khai bằng Docker."
echo "Bạn có thể truy cập qua địa chỉ IP của thiết bị hoặc qua http://$(hostname).local"
echo "Để xem logs, dùng lệnh: cd $INSTALL_DIR && docker-compose logs -f"
echo "Để dừng ứng dụng, dùng lệnh: cd $INSTALL_DIR && docker-compose down"



