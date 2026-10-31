# Kiến trúc ứng dụng

## Bố cục ứng dụng

Ứng dụng Python đặt tại `src/drowsyalert/`, chia theo phát hiện, đặc trưng, model, pipeline và tiện ích. `demo/` cung cấp entry point; `scripts/` xử lý chuẩn bị dữ liệu, huấn luyện, chú thích và đánh giá. Cấu hình runtime ở `configs/`; kiểm thử ở `tests/`.

## Trách nhiệm và chiều phụ thuộc

- `detection`: phát hiện mặt, landmark và vùng mắt.
- `features`: EAR, trạng thái mắt, PERCLOS, ngáp và head pose.
- `models`: suy luận EAR/CNN, dữ liệu và huấn luyện CNN.
- `pipeline`: nguồn video, quyết định, cảnh báo và điều phối xử lý.
- `utils`: cấu hình, overlay và thành phần hỗ trợ.

Phụ thuộc hướng vào các thành phần nền tảng; module phát hiện/đặc trưng không phụ thuộc giao diện demo. Scripts gọi logic package thay vì nhân bản thuật toán. Cấu hình và đầu vào được truyền tường minh.

## Luồng dữ liệu runtime

Nguồn webcam/video phát frame kèm timestamp; detector tìm mặt/landmark; bộ trích đặc trưng xác định trạng thái mắt và tín hiệu phụ; bộ tổng hợp thời gian tính PERCLOS/coverage; bộ quyết định tạo `NORMAL`, `ALERT` hoặc `UNKNOWN`; lớp trình bày hiển thị overlay và tùy chọn âm thanh. CSV/JSON lưu số đo và metadata, không lưu pixel frame theo mặc định.

## Dữ liệu và artifact sinh ra

Dataset, model tải về/checkpoint và kết quả thí nghiệm nằm trong thư mục cục bộ bị ignore. Không commit video cá nhân hoặc dữ liệu người tham gia. Artifact cần truy vết ghi hash, cấu hình, nguồn và trạng thái; chỉ lưu các trường scalar cần thiết.

## Quy tắc bảo trì

Giữ ranh giới module rõ ràng, tránh nhân đôi logic, duy trì kiểm thử ở cùng tầng với hành vi, và cập nhật tài liệu khi thay đổi luồng hoặc giao diện sử dụng. Đây là prototype nghiên cứu, không phải thiết bị an toàn được chứng nhận.
