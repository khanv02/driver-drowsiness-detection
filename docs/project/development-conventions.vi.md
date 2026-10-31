# Quy ước phát triển

## Cấu hình

Giữ giá trị mặc định trong cấu hình có cấu trúc, xác thực kiểu/miền giá trị và truyền cấu hình đã phân giải xuyên suốt lượt chạy. Ghi lại thiết lập ảnh hưởng kết quả để có thể tái lập. Ngưỡng nghiên cứu không được mô tả là ngưỡng an toàn đã chứng nhận.

## Tổ chức kiểm thử

Đặt test trong `tests/`, nhóm theo thành phần/hành vi. Kiểm thử tự động cần xác định, không phụ thuộc webcam, loa, mạng hoặc dữ liệu cá nhân. Test dữ liệu cần fixture nhỏ và được phép; kiểm tra thiết bị thật được ghi riêng là manual acceptance.

Lệnh dự án:

```powershell
uv run ruff check src scripts demo tests
uv run pytest
```

## Dữ liệu, model và kết quả

Giữ dữ liệu thô/đã xử lý, video người tham gia, model tải về, checkpoint và output sinh ra ngoài Git. Chỉ theo dõi README và placeholder rỗng phù hợp. Không đưa bí mật hoặc dữ liệu nhận dạng vào log, manifest công khai hay hồ sơ thí nghiệm.

## Quy trình task và nhánh

Theo danh sách chuẩn trong `specs/001-drowsyalert/tasks.md`; dùng ID ổn định, tôn trọng dependencies và gate. Tách công việc thành nhánh ngắn hạn, kiểm tra diff và xác minh trước khi tích hợp. Không viết lại lịch sử nhánh dùng chung hoặc dùng `git reset --hard` để phục hồi.

## Xác minh Phase 1

Ghi lại phiên bản Python/uv, trạng thái lock/dependency, model/dữ liệu sẵn có và giới hạn môi trường bằng lệnh có thể tái lập. Phân biệt dữ kiện đã quan sát với kế hoạch hoặc giả định; không ghi thông tin máy không cần thiết.
