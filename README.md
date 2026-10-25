# DrowsyAlert

<p align="center">
  <a href="https://www.python.org/"><img alt="Python 3.12" src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white"></a>
  <a href="https://opencv.org/"><img alt="OpenCV" src="https://img.shields.io/badge/OpenCV-4.x-5C3EE8?logo=opencv&logoColor=white"></a>
  <a href="https://ai.google.dev/edge/mediapipe/solutions/vision/face_landmarker"><img alt="MediaPipe" src="https://img.shields.io/badge/MediaPipe-Face%20Landmarker-0097A7?logo=google&logoColor=white"></a>
  <a href="https://pytorch.org/"><img alt="PyTorch optional" src="https://img.shields.io/badge/PyTorch-optional-EE4C2C?logo=pytorch&logoColor=white"></a>
  <a href="https://numpy.org/"><img alt="NumPy" src="https://img.shields.io/badge/NumPy-1.26%2B-013243?logo=numpy&logoColor=white"></a>
  <a href="https://pyyaml.org/"><img alt="PyYAML" src="https://img.shields.io/badge/PyYAML-6%2B-CC0000"></a>
  <a href="https://docs.astral.sh/uv/"><img alt="uv" src="https://img.shields.io/badge/uv-package%20manager-DE5FE9"></a>
  <a href="https://pytest.org/"><img alt="pytest" src="https://img.shields.io/badge/pytest-tests-0A9EDC?logo=pytest&logoColor=white"></a>
  <a href="https://docs.astral.sh/ruff/"><img alt="Ruff" src="https://img.shields.io/badge/Ruff-linting-D7FF64?logo=ruff&logoColor=black"></a>
</p>

## Giới thiệu

DrowsyAlert là ứng dụng nghiên cứu nhận biết dấu hiệu buồn ngủ qua webcam hoặc video. Hệ thống theo dõi trạng thái mắt, tính PERCLOS theo thời gian và hỗ trợ so sánh với dấu hiệu ngáp hoặc tư thế đầu. Khi chạy trực tiếp, ứng dụng hiển thị trạng thái và có thể phát cảnh báo âm thanh.

Đây là công cụ nghiên cứu tham khảo, không phải thiết bị an toàn được chứng nhận hay thiết bị chẩn đoán y tế. Ứng dụng không thay thế các biện pháp an toàn giao thông chính thức. Mục tiêu Accuracy ≥ 0,90 là mục tiêu nghiên cứu, chưa phải kết quả đã đạt.

## Chức năng

- Nhận hình từ webcam cục bộ hoặc đọc video có timestamp.
- Phát hiện khuôn mặt và landmark; cắt vùng mắt.
- Ước lượng trạng thái mắt bằng EAR (mặc định) hoặc CNN tùy chọn.
- Tính PERCLOS có trọng số thời gian, theo dõi nhắm mắt kéo dài và giữ trạng thái không xác định khi mất quan sát.
- Chọn một trong ba phương pháp: `perclos`, `perclos-yawn`, `perclos-head-pose`.
- Hiển thị overlay, ghi log CSV tùy chọn, chạy headless với video.
- Phát âm thanh cảnh báo trên Windows; video replay không phát âm thanh.

Model Face Landmarker và checkpoint CNN không được lưu trong Git. EAR không cần checkpoint CNN. Chế độ CNN cần cài PyTorch và cung cấp checkpoint tương thích.

## Công nghệ

| Nhóm | Công nghệ | Vai trò |
|---|---|---|
| Ngôn ngữ | Python 3.12 | Ứng dụng và công cụ nghiên cứu |
| Thị giác máy tính | OpenCV, MediaPipe | Đọc video, phát hiện landmark, xử lý vùng mắt |
| Tính toán | NumPy, PyYAML | Tính toán mảng và cấu hình YAML |
| CNN (tùy chọn) | PyTorch | Huấn luyện và suy luận phân loại mắt |
| Chuẩn bị/đánh giá dữ liệu | Pillow, scikit-learn, Matplotlib | Gói `train` tùy chọn |
| Công cụ phát triển | uv, pytest, Ruff | Quản lý môi trường, kiểm thử và lint |

Các huy hiệu phía trên là liên kết tới trang chính thức của từng công nghệ. Dependency thực tế được khai báo trong [`pyproject.toml`](pyproject.toml); phiên bản Python được chọn tại [`.python-version`](.python-version).

## Cài đặt và chạy

Cần Python 3.12 và [uv](https://docs.astral.sh/uv/). Từ thư mục gốc dự án:

```powershell
uv sync
uv run drowsyalert --download-model
uv run drowsyalert --camera 0 --eye-backend ear
```

Lần đầu tải Face Landmarker cần kết nối mạng. Sau đó xử lý webcam dùng model cục bộ.

### Chạy với CNN

```powershell
uv sync --extra cnn
uv run drowsyalert --camera 0 --eye-backend cnn --checkpoint models/checkpoints/eye_cnn.pt
```

### Chạy video và chọn phương pháp

```powershell
uv run drowsyalert --video path/to/video.mp4 --headless --log outputs/logs/run.csv
uv run drowsyalert --camera 0 --method perclos
uv run drowsyalert --camera 0 --method perclos-yawn
uv run drowsyalert --camera 0 --method perclos-head-pose
```

Cấu hình mặc định nằm ở [`configs/config.yaml`](configs/config.yaml). Các ngưỡng trong file là giá trị cấu hình ban đầu, chưa được xác nhận là ngưỡng an toàn cho tài xế. Xem `uv run drowsyalert --help` để biết các tùy chọn khác.

## Chuẩn bị dữ liệu và huấn luyện CNN

Kiểm tra nguồn, điều khoản sử dụng, nhãn và cấu trúc dataset trước khi huấn luyện. Script tải dataset có thể không hoạt động nếu nguồn thay đổi hoặc quyền truy cập/giấy phép không phù hợp. Không đưa dữ liệu tình nguyện viên hoặc dữ liệu cá nhân vào Git.

```powershell
uv sync --extra train
uv run python scripts/download_dataset.py
uv run python scripts/prepare_dataset.py --input data/raw/kaggle --output data/processed --seed 42
uv run python scripts/train_model.py --manifest data/processed/manifest.csv --checkpoint models/checkpoints/eye_cnn.pt --output outputs/results/eye_cnn
```

Nếu có metadata người/phiên, truyền thêm `--groups` với CSV gồm cột `source,group_id`. Nếu không có metadata này, cách nhóm nguồn và phát hiện ảnh trùng không đảm bảo tách độc lập theo người. Chỉ dùng tập test để đánh giá cuối, không dùng để chọn model hoặc ngưỡng.

## Kiểm thử

```powershell
uv run ruff check src scripts demo tests
uv run pytest
```

Test tự động bao phủ một số trường hợp hình học, thời gian, cấu hình, dữ liệu và cảnh báo. Test đạt không chứng minh độ chính xác thực tế. Kiểm tra webcam và âm thanh cần thiết bị thật, nên ghi kết quả riêng.

## Cấu trúc dự án

```text
.
├── configs/                 # Cấu hình chạy
├── data/                    # Dataset cục bộ, không commit dữ liệu
├── demo/                    # Entry point demo
├── docs/                    # Kiến trúc và tài liệu đề tài
├── .specify/                # Constitution và cấu hình Spec Kit
├── models/                  # Model tải về và checkpoint cục bộ
├── outputs/                 # Kết quả, biểu đồ và log sinh tự động
├── scripts/                 # Tải/chuẩn bị dữ liệu, huấn luyện
├── src/drowsyalert/
│   ├── detection/           # Khuôn mặt và landmark
│   ├── features/            # Hình học, PERCLOS, ngáp, tư thế đầu
│   ├── models/              # EAR/CNN, huấn luyện và dữ liệu
│   ├── pipeline/            # Nguồn video, quyết định, cảnh báo
│   └── utils/               # Cấu hình và overlay
├── tests/                   # Kiểm thử tự động
├── specs/                   # Đặc tả và task breakdown
└── plan/                    # Kế hoạch và backlog nghiên cứu
```

## Tài liệu và quyền riêng tư

- [Mô tả đề tài 12](docs/de-tai-12-drowsyalert.md)
- [Phiếu mô tả đề tài gốc](docs/PhieuMoTaDeTai_30DeTai_ThiGiacMayTinh_NCKH.docx)
- [Kiến trúc ứng dụng](docs/architecture.md)
- [Project Constitution](.specify/memory/constitution.md)
- [Implementation plan](specs/001-drowsyalert/plan.md)
- [Research decisions](specs/001-drowsyalert/research.md)
- [Đặc tả yêu cầu](specs/001-drowsyalert/spec.md)
- [Danh sách công việc](specs/001-drowsyalert/tasks.md)

Dữ liệu ở `data/`, model ở `models/` và kết quả ở `outputs/` được loại khỏi Git; chỉ README và `.gitkeep` được giữ. Webcam được xử lý cục bộ mặc định. Việc thu thập video tình nguyện viên cần có đồng ý và tuân thủ hướng dẫn của đơn vị phụ trách.

## Nhóm phát triển

- Phạm Nguyễn Phúc Khang
- Huỳnh Vĩnh Lợi
- Dương Công Khoa
- Cao Thanh Hùng

## Giấy phép

Dự án được phát hành theo [Giấy phép MIT](LICENSE).
