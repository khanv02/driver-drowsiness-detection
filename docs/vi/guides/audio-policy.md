# Quy tắc cảnh báo âm thanh

Âm thanh là hiệu ứng trình bày khi chạy trực tiếp. Việc phát hiện và trạng thái quyết định không phụ thuộc vào loa có sẵn hay phát âm thanh thành công hay không.

- `ALERT` trực tiếp đầu tiên yêu cầu phát âm thanh bất đồng bộ ngay lập tức.
- Cảnh báo kéo dài chỉ được phát lại khi đã hết `cooldown_seconds`.
- Khi trở về `NORMAL` hoặc `UNKNOWN`, âm thanh đang phát sẽ dừng.
- Cảnh báo mới trong thời gian cooldown vẫn hiển thị nhưng không phát lại sớm.
- `--mute` tắt âm thanh mà không đổi xử lý mắt, thời gian hay quyết định.
- Phát lại video đã ghi luôn im lặng để thí nghiệm không phát âm thanh.
- Thiếu tệp âm thanh hoặc lỗi phát/dừng được ghi nhận, không làm đổi quyết định.

Tóm tắt mỗi lượt chạy ghi âm thanh có được bật và khả dụng không, chính sách live/mute/replay, số lần phát và lỗi, cooldown, định danh âm thanh và lỗi gần nhất. Âm thanh qua loa thực tế vẫn cần kiểm tra phần cứng thủ công Phase 4.
