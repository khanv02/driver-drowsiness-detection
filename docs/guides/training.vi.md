# Quy trình huấn luyện EyeCNN

**Trạng thái:** Đã hoàn tất huấn luyện CEW và một lần đánh giá held-out đã khóa. Bộ phân loại ảnh đạt mục tiêu Accuracy quy định; đây không phải kết quả phát hiện buồn ngủ ở cấp video.

## Môi trường và đầu vào

Cài các dependency huấn luyện đã khóa:

```powershell
uv sync --extra train
```

Đầu vào phải là `manifest.csv` đã được xác thực và tạo bởi lệnh chuẩn bị dữ liệu Phase 3. Loader từ chối thiếu trường schema, nhãn/hash/split sai, đường dẫn trùng, nhóm xuất hiện ở nhiều split và split thiếu một trong hai lớp. Trước khi huấn luyện, ghi lại SHA-256 của manifest từ `dataset.json`.

## Lệnh tái lập

Lệnh huấn luyện cuối:

```powershell
uv run python scripts/train_model.py `
  --manifest data/processed/manifest.csv `
  --checkpoint models/checkpoints/eye_cnn_50.pt `
  --output outputs/results/eye_cnn-training-50 `
  --epochs 50 `
  --batch-size 64 `
  --patience 5 `
  --learning-rate 0.001 `
  --seed 42 `
  --device cpu
```

`models/checkpoints/` và `outputs/results/` là nơi lưu artifact bị Git bỏ qua. Không commit model đã huấn luyện hoặc đầu ra lượt chạy.

## Hợp đồng model và tiền xử lý cố định

- Lớp: chỉ số 0 `open`, chỉ số 1 `closed`.
- Đầu vào: crop mắt BGR đổi kích thước 64 × 64, chuyển thành RGB CHW float32 trong [0, 1].
- Mạng: ba khối Conv/ReLU/MaxPool (32, 64, 128 kênh), adaptive average pool, dropout 0.3 và bộ phân loại tuyến tính hai logit.
- Bộ tối ưu: Adam; hàm mất mát: cross entropy.
- Tăng cường dữ liệu chỉ trên train: hệ số sáng 0.8–1.2, xoay -8 đến +8 độ.
- Seed điều khiển Python, NumPy, Torch, loader được xáo trộn và thuật toán Torch xác định.

## Quy tắc chọn model và artifact

Đánh giá trên validation sau mỗi epoch. Chỉ thay checkpoint khi macro F1 validation tăng nghiêm ngặt; dừng sớm sau `patience` epoch không cải thiện. Huấn luyện không tạo hoặc đo split test.

- `run_config.json`: đầu vào đã phân giải, hash manifest, seed, thiết bị, siêu tham số, số mẫu, tăng cường dữ liệu và metric chọn model.
- `history.json`: loss train và Accuracy/macro F1 validation theo epoch.
- `eye_cnn.pt`: hợp đồng kiến trúc/tiền xử lý, state dictionary, định danh manifest, seed, epoch được chọn, điểm validation và thiết lập huấn luyện.

Giữ kín test cho đến khi khóa checkpoint và ngưỡng suy luận. Sau khi khóa, chạy đánh giá held-out đúng một lần vào thư mục kết quả mới:

```powershell
uv run python scripts/evaluate_model.py `
  --manifest data/processed/manifest.csv `
  --checkpoint models/checkpoints/eye_cnn.pt `
  --output outputs/results/eye_cnn-heldout `
  --threshold 0.5 `
  --device auto
```

Evaluator xác minh checkpoint được chọn bằng validation từ đúng manifest; ghi hash checkpoint/manifest, số lượng, Accuracy, confusion matrix, Precision/Recall/F1 từng lớp, macro F1 và việc Accuracy có đạt >= 0.90 hay không. Không ghi đè `metrics.json` đã tồn tại. Smoke run tổng hợp thành công chỉ chứng minh luồng và tính tương thích checkpoint, không chứng minh chất lượng model hay hiệu quả phát hiện buồn ngủ thực tế.

## Kết quả huấn luyện và held-out CEW

Lần chạy đầu chỉ dùng validation đặt mục tiêu 30 epoch. Checkpoint tốt nhất ở epoch 30 nên tăng ngân sách huấn luyện trước khi mở test. Ứng viên xác định 50 epoch tái tạo chính xác epoch 1–30, dừng sau epoch 39 và chọn epoch 34.

- Accuracy validation cuối: 0.877410.
- Macro F1 validation cuối: 0.877056.
- Diễn biến: loss tiếp tục giảm sau khi validation ngừng cải thiện; patience 5 khôi phục checkpoint epoch 34 và ngăn fit thêm.
- Ngưỡng cố định: xác suất closed >= 0.5; không tìm ngưỡng trên test.
- Ảnh held-out: 728 (376 open, 352 closed).
- Accuracy held-out: **0.907967**; đạt mục tiêu >= 0.90.
- Macro F1 held-out: **0.907904**.
- Open Precision/Recall/F1: 0.916442 / 0.904255 / 0.910308.
- Closed Precision/Recall/F1: 0.899160 / 0.911932 / 0.905501.
- Confusion matrix (hàng `actual`, cột `predicted`; open rồi closed): `[[340, 36], [31, 321]]`.

Định danh artifact:

- SHA-256 manifest: `42ebc450eba138301f13df4cd06736b31dab20b7d2fa55464251ed87c765c58f`.
- SHA-256 checkpoint cuối: `40f39307be277e61201c303c85dc2542dc81ab6593958f06c85b1a9bf8befd85`.
- SHA-256 cấu hình lượt chạy: `80b3d53f7ec2d76e3202a4a06e69bd079789fe47b09a1eb114369ed0967e9dc5`.
- SHA-256 lịch sử huấn luyện: `e128a7d1cd23bb1f17ff1860dd04e243cbac70aff41610d693c8e8ee722d2bc7`.
- SHA-256 metric held-out: `ddc1fa1db6b91c9f2e23cd4e14daee6d475aa816c7b9adae06fe4ca72e9699bf`.

Checkpoint và kết quả sinh ra vẫn nằm trong thư mục artifact cục bộ bị ignore. Nhiễu miền nguồn CEW và cách nhóm cặp dựa trên tên file vẫn giới hạn khả năng khái quát hóa.

## Chính sách độ tin cậy khi chạy

Suy luận CNN được ghi nguồn `cnn_eye_classifier`; không thay thế định danh `landmark_ear`. Mỗi mắt hợp lệ có xác suất nhắm riêng. Với mặc định `cnn_threshold: 0.5` và `cnn_uncertainty_margin: 0.1`, xác suất <= 0.4 được coi là mở chắc chắn, >= 0.6 là nhắm chắc chắn, nằm giữa là không xác định. Một mắt mở chắc chắn đủ xác lập quan sát mở; trạng thái nhắm cần cả hai mắt nhắm chắc chắn. Bằng chứng không chắc chắn hoặc chỉ một mắt nhắm vẫn là không xác định.

Mỗi summary và dòng CSV runtime ghi nguồn, ngưỡng, biên không chắc chắn và SHA-256 checkpoint. Checkpoint thiếu hoặc không tương thích gây lỗi tường minh; ứng dụng không chuyển sang EAR rồi tuyên bố đó là bằng chứng CNN.
