# Quy ước hồ sơ thí nghiệm

DrowsyAlert có thể ghi hai artifact cục bộ bổ sung cho nhau: `--log <path.csv>` lưu các trường bằng chứng ổn định theo frame để kiểm tra; `--record <path.json>` lưu metadata lượt chạy có phiên bản schema cùng các bản ghi frame dạng scalar. Không artifact nào chứa pixel frame hay crop mắt. Kết quả được sinh dưới `outputs/` và bị Git bỏ qua. JSON hiện có không bị âm thầm ghi đè.

```powershell
uv run drowsyalert --video <permitted-clip.mp4> --headless --mute `
  --method perclos-yawn `
  --dataset-id <dataset-version> --split-id <split-manifest-id> `
  --seed 42 --code-revision <git-commit> `
  --log outputs/logs/clip-001.csv `
  --record outputs/results/clip-001.json
```

JSON lưu phiên bản schema, run ID xác định, giờ UTC, trạng thái hoàn tất/lỗi; revision package/mã và môi trường không định danh; dataset/split ID, source ID an toàn quyền riêng tư và hash video; phương pháp A/B/C, cấu hình chung/tín hiệu phụ; hash và nội dung cấu hình đã phân giải; nguồn mắt/ngưỡng/hash checkpoint tùy chọn/tên model khuôn mặt; seed/chính sách âm thanh; quan sát scalar từng frame, bằng chứng thời gian/tín hiệu, quyết định và thời gian xử lý; số frame, thời gian thực và thông lượng.

Run ID là hash của giờ tạo đã khai báo và định danh khoa học. Cùng đầu vào và giờ tạo cho cùng ID; đổi cấu hình hoặc định danh sẽ đổi ID. Demo không chính thức có thể thiếu dataset ID, split ID hoặc revision mã; khi đó `provenance_complete=false` liệt kê trường thiếu và không được coi là bằng chứng nghiên cứu hoàn chỉnh.

Camera dùng source ID `camera:<index>` không chứa dữ liệu cá nhân. Video dùng ID suy ra từ hash nội dung và lưu SHA-256 đầy đủ, không lộ tên tệp hay đường dẫn tuyệt đối. Không thêm ảnh thô, tên người tham gia hoặc đường dẫn cục bộ. Manifest dataset riêng tư được duyệt ánh xạ hash nội dung sang clip ID được phép.

Nếu xử lý lỗi sau khi tạo hồ sơ, trạng thái JSON là `error`; giữ các frame scalar đã hoàn tất và ghi loại/nội dung exception. Không gắn nhãn lượt chạy là hoàn tất. Metric và kết luận so sánh thuộc Phase 6, cần dataset thời gian và protocol đánh giá đã duyệt.
