# Quy tắc quyết định phương pháp A

Phương pháp A của Phase 4 kết hợp bằng chứng nhắm mắt liên tục tức thời với cửa sổ PERCLOS đã sẵn sàng. Kết hợp tín hiệu phương pháp B/C được để lại cho Phase 5 T-021.

## Thứ tự ưu tiên quyết định

1. Quan sát mắt không xác định trả về `UNKNOWN`, lý do `Eyes unavailable`.
2. Bằng chứng theo thời gian không hợp lệ hoặc không hữu hạn trả về `UNKNOWN`.
3. Nhắm mắt liên tục đạt hoặc vượt `closed_seconds` trả về `ALERT`, kể cả khi cửa sổ PERCLOS đang khởi động.
4. Thời lượng hợp lệ/coverage chưa đủ trả về `UNKNOWN` với lý do khởi động.
5. Cửa sổ sẵn sàng nhưng không có PERCLOS trả về `UNKNOWN`.
6. PERCLOS đạt hoặc vượt `perclos_threshold` trả về `ALERT`.
7. PERCLOS hợp lệ dưới ngưỡng trong cửa sổ sẵn sàng trả về `NORMAL`.

So sánh bằng ngưỡng được tính là cảnh báo. Bằng chứng thiếu hoặc không hợp lệ không bao giờ được coi là `NORMAL`. Giá trị mặc định hiện tại phục vụ đánh giá nghiên cứu, không phải ngưỡng an toàn tài xế đã chứng nhận.

## Cấu hình được ghi nhận

Mỗi kết quả chạy lưu các giá trị đã phân giải của `closed_seconds`, `window_seconds`, `min_valid_seconds`, `min_coverage`, `max_gap_seconds` và `perclos_threshold` cùng cấu hình còn lại. CSV từng frame gồm thời lượng nhắm mắt, PERCLOS, coverage, thời lượng hợp lệ, trạng thái sẵn sàng, trạng thái và lý do.
