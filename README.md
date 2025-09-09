Trình Quản Lý WiFi cho Orange Pi (Phiên bản Docker)
Dự án này cung cấp một giao diện web đơn giản để cấu hình và quản lý kết nối WiFi trên các thiết bị máy tính nhúng như Orange Pi, đặc biệt hữu ích cho việc cài đặt không cần màn hình và bàn phím (headless setup).

Toàn bộ ứng dụng được đóng gói trong một Docker container, giúp việc cài đặt, quản lý và gỡ bỏ trở nên cực kỳ sạch sẽ và dễ dàng.

✨ Tính năng chính
Giao diện Web trực quan: Dễ dàng quét các mạng WiFi có sẵn và kết nối.

Trang Trạng thái: Hiển thị thông tin kết nối hiện tại, bao gồm Tên mạng (SSID) và địa chỉ IP.

Triển khai bằng Docker: Đóng gói toàn bộ ứng dụng và môi trường, không làm ảnh hưởng đến hệ điều hành chính.

Cài đặt bằng một dòng lệnh: Kịch bản cài đặt tự động hóa toàn bộ quá trình.

Tự động khởi động: Ứng dụng tự khởi chạy mỗi khi thiết bị reboot.

Quản lý từ xa: Điều khiển kết nối mạng của Orange Pi từ bất kỳ thiết bị nào trong cùng mạng LAN.

📋 Yêu cầu
Một bo mạch Orange Pi (hoặc Raspberry Pi, hoặc các SBC khác).

Thẻ nhớ đã cài đặt hệ điều hành Linux (khuyến nghị Armbian hoặc Debian).

Quyền truy cập root hoặc sudo.

Kết nối Internet ban đầu để tải về và cài đặt (có thể dùng dây Ethernet).

🚀 Hướng dẫn Cài đặt
Quá trình cài đặt được tự động hóa hoàn toàn.

Bước 1: Chuẩn bị Repository của bạn
Fork hoặc tạo một repository mới trên GitHub của bạn.

Tải 5 file của dự án này lên repository đó:

app.py

requirements.txt

Dockerfile

docker-compose.yml

install.sh

Chỉnh sửa file install.sh: Mở file install.sh trên GitHub của bạn và thay đổi 2 dòng sau đây thành tên người dùng và tên repository của bạn:

GIT_USERNAME="YOUR_USERNAME"
GIT_REPO="YOUR_REPO"

Bước 2: Chạy lệnh cài đặt
Mở terminal trên Orange Pi của bạn và chạy lệnh duy nhất dưới đây. (Hãy chắc chắn bạn đã thay YOUR_USERNAME và YOUR_REPO trong lệnh này).

curl -sL [https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/install.sh](https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/install.sh) | sudo bash

Kịch bản sẽ tự động thực hiện các công việc sau:

Cài đặt Docker và Docker Compose nếu cần.

Tải mã nguồn từ repository GitHub của bạn.

Build Docker image.

Khởi chạy ứng dụng.

💻 Cách sử dụng
Sau khi cài đặt thành công, bạn có thể truy cập giao diện web quản lý bằng cách mở trình duyệt trên điện thoại hoặc máy tính trong cùng mạng và truy cập vào địa chỉ IP của Orange Pi.

Ví dụ: http://192.168.1.10

Bạn có thể tìm địa chỉ IP của Orange Pi bằng cách xem trong trang quản trị của router.

🐳 Quản lý ứng dụng (Docker)
Vì ứng dụng chạy trong Docker, bạn có thể dễ dàng quản lý nó bằng các lệnh sau. Bạn cần cd vào thư mục cài đặt trước:

cd /opt/orangepi-wifi-manager

Xem logs (nhật ký) của ứng dụng:

docker-compose logs -f

Dừng ứng dụng:

docker-compose down

Khởi động lại ứng dụng:

docker-compose up -d

Cập nhật phiên bản mới (sau khi bạn đã push code mới lên GitHub):

git pull && docker-compose up -d --build

📝 License
Dự án này được cấp phép dưới giấy phép MIT. Xem file LICENSE để biết thêm chi tiết.