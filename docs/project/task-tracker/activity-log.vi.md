# Nhật ký hoạt động DrowsyAlert

Đây là nhật ký tài liệu dự án về artifact đã review và thay đổi repository; không phải lịch sử duyệt web cá nhân hay hoạt động ngoài repository.

## 2026-10-27 — Đối soát trạng thái

### Đã rà soát

- `.specify/memory/constitution.md`.
- `specs/001-drowsyalert/spec.md`, `plan.md`, `tasks.md`, `decisions.md`.
- Protocol đánh giá, kết quả validation, verification, bàn giao Phase 6, thẻ dataset và README.
- Nhánh Git hiện tại và trạng thái working tree.

### Thay đổi được ghi nhận

- Đối soát câu hỏi mở SPEC và độ sẵn sàng PLAN/TASKS theo NITYMED Protocol v1.1 đã duyệt và trạng thái Phase 6; không đổi hành vi yêu cầu.
- Sửa thông tin data-readiness cũ; tách lựa chọn nguồn/protocol đã duyệt khỏi chú thích và bằng chứng held-out còn chờ.
- Đối soát quyết định G0-05 đến G0-09 với đánh giá CEW hoàn tất, protocol NITYMED được duyệt, công việc ngưỡng còn lại và việc thu tình nguyện viên đang hoãn.
- Bỏ phụ thuộc webcam/âm thanh vật lý T-018 khỏi T-022; hoàn tất T-022 theo T-119–T-122, giữ nghiệm thu phần cứng riêng ở T-018.
- Cập nhật tổng kết G5, Phase 6 và số lượng task. Checklist chuẩn có 160 ID, 147 hoàn tất, 13 còn mở.
- Thêm bảng trạng thái task song ngữ; định nghĩa và tiêu chí nghiệm thu chuẩn vẫn ở `specs/001-drowsyalert/tasks.md`.
- Cập nhật README gốc với nghiệm thu phần mềm G5, công việc Phase 6 và liên kết tới tracker/nhật ký.
- Làm rõ bin System Accuracy: độ rộng và bước 1 giây, không chồng lấn bin kề; 0.50 là ngưỡng occupancy riêng trong bin.

### Trạng thái xác minh

- Đã kiểm tra hai bảng trạng thái có cùng 160 ID và khớp checkbox checklist chuẩn.
- `git diff --check` đạt.
- Không chạy test ứng dụng vì chỉ cập nhật tài liệu và trạng thái task. Nghiệm thu webcam/âm thanh vật lý và đánh giá A/B/C held-out vẫn chưa xác minh/còn mở.
- Đã đối chiếu làm rõ review trong Protocol §7, tài liệu metric, SPEC OQ-004 và quyết định G0-07; không đổi mã đánh giá hoặc kết quả chấm.
