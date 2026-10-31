# Thẻ dataset NITYMED

## Tổng quan và nguồn gốc

NITYMED HDTV720 là corpus video lái xe ban đêm được chọn làm nguồn dữ liệu Phase 6. Trang nhà cung cấp mô tả 130 video MP4 từ 21 người, gồm các nhóm ngáp và microsleep. Bản cục bộ được kiểm kê có 126 video; sai khác với thông tin nguồn phải được giữ trong manifest và hồ sơ audit, không tự suy đoán.

## Quyền truy cập và bảo quản

Nhà cung cấp yêu cầu biểu mẫu truy cập và ghi nhận Creative Commons Attribution. Lưu bằng chứng đã làm theo điều kiện nhà cung cấp, phiên bản archive và hash. Dữ liệu video giữ trong `data/` bị Git bỏ qua; không đưa clip, khung hình hay thông tin nhận dạng người tham gia vào Git hoặc hồ sơ công khai.

## Kiểm kê và nhãn

Bản HDTV720 cục bộ gồm 126 MP4, tổng 697,049,508 byte và 5,860.677 giây. Video giải mã ở 1280×720; 125 clip báo 25 FPS, một clip 24 FPS. Xem chi tiết manifest và sai khác tại audit dataset video.

Corpus chưa có chú thích onset/offset theo thời gian và chưa xác minh được ánh xạ clip-người tham gia. Vì vậy chưa phải corpus held-out được duyệt. Cần review nhãn độc lập theo media time và xác lập split trước đánh giá cuối.

## Giới hạn và sử dụng

Phân chia theo clip không đảm bảo độc lập theo người. Không dùng CEW hoặc video demo webcam thay cho nhãn sự kiện thời gian. Không có quyền thu video tình nguyện viên trong phạm vi hiện tại. Chỉ dùng validation để chọn cấu hình; test held-out cần được giữ kín cho đến khi protocol được khóa.
