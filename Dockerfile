# Sử dụng một base image Python nhẹ
FROM python:3.9-slim-buster

# Cài đặt các công cụ mạng cần thiết mà container không có sẵn
# network-manager cung cấp lệnh 'nmcli'
# wireless-tools cung cấp lệnh 'iwgetid'
RUN apt-get update && apt-get install -y \
    network-manager \
    wireless-tools \
    && rm -rf /var/lib/apt/lists/*

# Tạo thư mục làm việc cho ứng dụng
WORKDIR /app

# Sao chép file requirements.txt và cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn còn lại của ứng dụng vào thư mục làm việc
COPY . .

# Chạy ứng dụng bằng gunicorn khi container khởi động
CMD ["gunicorn", "--workers", "1", "--bind", "0.0.0.0:80", "app:app"]

