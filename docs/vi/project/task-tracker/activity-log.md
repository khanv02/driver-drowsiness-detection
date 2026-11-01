# Nhật ký hoạt động DrowsyAlert

Đây là nhật ký tài liệu dự án về artifact đã review và thay đổi repository; không phải lịch sử duyệt web cá nhân hay hoạt động ngoài repository.

## 2026-11-01 — Phát lại validation và sweep có giới hạn

### Đã rà soát

- `src/drowsyalert/experiments/batch.py`, `evaluation.py`, `records.py` và `replay.py`.
- Batch plan, run record, chú thích và comparison validation v1.1 đã lưu.
- `docs/en/guides/evaluation-execution.md` và bản tiếng Việt tương ứng.

### Thay đổi được ghi nhận

- Thêm phát lại tất định chỉ trên validation, tính lại trạng thái mắt, cửa sổ thời gian, ngáp, tư thế đầu và quyết định từ quan sát khung hình đã lưu mà không chạy lại face landmarker hoặc đọc video.
- Thêm lưới cấu hình có giới hạn, metric A/B/C theo từng ứng viên, hash cấu hình và chốt chặn chỉ cho validation, từ chối plan test và chú thích test.
- Thêm `scripts/replay_validation_sweep.py`, `load_batch_plan` và test replay tập trung.
- Đánh dấu T-157 hoàn thành và làm mới bảng trạng thái Anh/Việt: 171 mã task, 152 hoàn thành, 19 còn mở.

### Trạng thái xác minh

- Phát lại hồ sơ validation đã lưu với cấu hình v1.1 đóng băng cho kết quả A/B/C khớp chính xác comparison đã lưu: TP 5, FP 28, FN 14, F1 0.19230769230769232, coverage 0.629932320265611 và latency trung bình 2.904000000000001 giây cho A, B và C.
- `python -m pytest tests/test_experiment_replay.py tests/test_experiments.py -q` đạt 16 test.
- `python -m ruff check src scripts demo tests` đạt.
- `uv run` lỗi trampoline trong môi trường này, nên các kiểm tra được chạy trực tiếp qua virtual environment của repository.
- Công việc này chỉ dùng validation. Chưa tạo kết quả test held-out, cấu hình cuối đã khóa, hoặc tuyên bố báo cáo/slide.

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
