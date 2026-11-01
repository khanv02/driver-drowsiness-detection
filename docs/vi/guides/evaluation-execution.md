# Chạy đánh giá A/B/C có kiểm soát

Batch runner tạo một kế hoạch bất biến dùng chung cho A, B và C. Kế hoạch chứa danh sách clip chính xác, hash manifest NITYMED, split ID, revision mã, seed, nguồn landmark-EAR và một cấu hình đã phân giải dùng chung. Mỗi phương pháp chỉ khác tín hiệu phụ đã khai báo.

Runner không tạo kế hoạch nếu clip được chọn chưa `reviewed` hoặc chưa thuộc partition yêu cầu; đường dẫn manifest và worklist không khớp; nguồn mắt khác `landmark_ear`; thiếu thiết lập ngưỡng/cửa sổ/tín hiệu chung; C không có tham chiếu head pose dạng số đã khóa bằng validation; hoặc thiếu định danh dữ liệu/split/manifest/mã.

Mọi phát lại bị ép `headless=True`, `mute=True` và backend EAR. Hồ sơ lượt chạy dùng clip ID ổn định cùng SHA-256 nguồn thật. Chỉ tiếp tục hồ sơ có clip, hash, phương pháp, nguồn, backend mắt, trạng thái hoàn tất và chính sách âm thanh khớp; xung đột không tương thích bị từ chối, không ghi đè.

Sau T-126/T-139, chạy validation trước bằng cấu hình đánh giá riêng đã khóa:

```powershell
uv run python scripts/run_video_evaluation.py `
  --manifest data/processed/nitymed/video-manifest.csv `
  --worklist data/processed/nitymed/annotation-worklist.csv `
  --video-root data/raw/nitymed/DSM_Dataset-HDTV720 `
  --output outputs/results/nitymed-validation-v1 `
  --partition validation --split-id nitymed-split-v1 `
  --code-revision <git-commit> --seed 42 `
  --config configs/evaluation-v1.yaml
```

Không dùng nguyên cấu hình demo hiện tại: tham chiếu head pose là `null`, nên C có kiểm soát bị chặn cho đến khi validation xác định giá trị số.

Khi chú thích cuối và giá trị protocol được duyệt, bổ sung `--annotations data/processed/nitymed/annotations.csv`, `--early-tolerance 1.0 --late-tolerance 2.0`, `--bin-seconds 1.0 --positive-fraction 0.5` và `--reference-label microsleep`. Các giá trị này được cố định bởi Protocol `drowsyalert-video-eval-v1.1`. Bộ xuất so sánh nạp lại hồ sơ đã hoạch định, tính lại từng phương pháp trên cùng clip/chú thích và ghi JSON nghiêm ngặt. Có thể dùng validation chọn ngưỡng; tuyệt đối không dùng test held-out để tinh chỉnh.

## Phát lại validation ngoại tuyến và sweep có giới hạn

Khi đã có hồ sơ validation theo kế hoạch, bước phát lại tính lại trạng thái mắt, cửa sổ thời gian, ngáp, tư thế đầu và quyết định từ các quan sát khung hình đã lưu. Bước này không chạy lại face landmarker, không đọc video và từ chối partition test hoặc chú thích test. Mọi ứng viên dùng cùng bộ hồ sơ, chú thích, protocol và định danh kế hoạch.

```powershell
uv run python scripts/replay_validation_sweep.py `
  --plan outputs/results/nitymed-validation-v1.1/batch-plan.json `
  --annotations data/processed/nitymed/validation-annotations-v1.1.csv `
  --output outputs/results/nitymed-validation-v1.1/sweep.json `
  --early-tolerance 1.0 --late-tolerance 2.0 `
  --bin-seconds 1.0 --positive-fraction 0.5 `
  --reference-label microsleep
```

Lưới mặc định đã khai báo trước thay đổi cửa sổ thời gian, thời lượng warm-up, coverage tối thiểu, ngưỡng PERCLOS, ngưỡng nhắm mắt kéo dài và ngưỡng EAR. Lưới bị giới hạn ở 350 tổ hợp; các tổ hợp không hợp lệ như warm-up dài hơn cửa sổ bị bỏ qua. Mỗi ứng viên trong output chứa cấu hình đã phân giải đầy đủ, SHA-256 cấu hình, metric A/B/C theo từng phương pháp và một bản tổng hợp. T-158 chọn từ output validation này; tuyệt đối không trỏ sweep vào hồ sơ held-out.
