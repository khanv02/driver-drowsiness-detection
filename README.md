<h1 align="center">🚗💤 DrowsyAlert</h1>

<p align="center">CNN-based Driver Drowsiness Detection Research Prototype</p>

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

Đây là công cụ nghiên cứu tham khảo, không phải thiết bị an toàn được chứng nhận hay thiết bị chẩn đoán y tế. Ứng dụng không thay thế các biện pháp an toàn giao thông chính thức. Trên tập test CEW, CNN đạt Accuracy 0,907967 cho phân loại ảnh mắt; đây không phải kết quả phát hiện buồn ngủ trên video, bằng chứng an toàn đường bộ hay kết quả tổng quát hóa sang tài xế thực tế.

## Chức năng

- Nhận hình từ webcam cục bộ hoặc đọc video có timestamp.
- Phát hiện khuôn mặt và landmark; cắt vùng mắt.
- Ước lượng trạng thái mắt bằng EAR (mặc định) hoặc CNN tùy chọn.
- Tính PERCLOS có trọng số thời gian, theo dõi nhắm mắt kéo dài và giữ trạng thái không xác định khi mất quan sát.
- Chọn một trong ba phương pháp: `perclos`, `perclos-yawn`, `perclos-head-pose`.
- Hiển thị overlay, ghi log CSV tùy chọn, chạy headless với video.
- Phát âm thanh cảnh báo trên Windows; video replay không phát âm thanh.

Model Face Landmarker và checkpoint CNN không được lưu trong Git. EAR không cần checkpoint CNN. Chế độ CNN cần cài PyTorch và cung cấp checkpoint tương thích.

## Trạng thái phát triển

**Phase 1 — Foundation: hoàn thành (G1).** Nền tảng dự án, quy ước kiểm thử, quản lý cấu hình và ranh giới dữ liệu riêng tư đã được thiết lập.

**Phase 2 — Landmark và PERCLOS baseline: hoàn thành (G2).** Pipeline webcam/video có timestamp; kiểm tra tính hợp lệ riêng cho khuôn mặt và từng mắt; trạng thái mắt `OPEN`/`CLOSED`/`UNKNOWN` từ EAR; PERCLOS theo thời gian có coverage/readiness và xử lý khoảng mất quan sát. Replay headless tái lập được và xuất metadata.

**Phase 3 — CNN eye classification: hoàn thành (G3).** Dataset CEW được chuẩn bị theo split nhóm, CNN được chọn checkpoint bằng validation và đánh giá một lần trên tập test đã đóng băng. Trên 728 ảnh test, mô hình đạt Accuracy **0,907967** và macro F1 **0,907904**. G3 đã vượt qua 79 kiểm thử tự động; Ruff đạt.

**Phase 4 — Real-time drowsiness alert: triển khai hoàn thành; nghiệm thu G4 đang chờ.** Đã tích hợp quyết định cảnh báo Method A, overlay trạng thái/lý do, điều khiển âm thanh có cooldown và mute, xử lý UNKNOWN, cùng luồng live và CLI. Bộ kiểm thử tự động có **112 passed** và Ruff đạt. Smoke test webcam đã đọc 5 khung hình CNN ở chế độ headless/mute; bước này chỉ xác nhận capture và metadata, chưa xác nhận hiển thị giao diện hoặc âm thanh. G4 cần người kiểm tra trực tiếp các chuyển trạng thái, phục hồi, thao tác dừng và cảnh báo âm thanh.

Kết quả Phase 3 chỉ đo phân loại ảnh mắt trên CEW; Phase 4 xác minh luồng ứng dụng/cảnh báo và smoke test capture, không chứng minh độ chính xác phát hiện buồn ngủ theo video, hiệu quả cảnh báo ngoài thực tế, an toàn lái xe hay tổng quát hóa sang tài xế. So sánh nghiên cứu PERCLOS, PERCLOS + yawning và PERCLOS + head pose vẫn cần thực hiện ở các giai đoạn sau. Xem [bằng chứng kiểm thử và kết quả](docs/verification.md), [quy trình huấn luyện](docs/training.md) và [danh sách công việc](specs/001-drowsyalert/tasks.md).

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

### Trạng thái và điều khiển webcam

- `NORMAL`: quan sát hợp lệ, cửa sổ PERCLOS đã sẵn sàng và chưa đạt ngưỡng cảnh báo.
- `ALERT`: nhắm mắt liên tục đủ lâu hoặc PERCLOS đạt ngưỡng; lý do cụ thể hiển thị trên cửa sổ.
- `UNKNOWN`: không thấy khuôn mặt/mắt, dự đoán không chắc chắn, dữ liệu thời gian không hợp lệ hoặc cửa sổ vẫn đang khởi động. `UNKNOWN` không được coi là `NORMAL`.
- Nhấn `Q` hoặc `Esc` để dừng. Thêm `--mute` để tắt âm thanh mà không thay đổi quyết định.
- Khung hình webcam được xử lý cục bộ và không được lưu bởi luồng demo. `--log` chỉ ghi số đo/trạng thái CSV, không ghi video.

Overlay luôn hiển thị nguồn trạng thái mắt, trạng thái/lý do, PERCLOS/coverage, điều khiển dừng và thông báo đây là prototype nghiên cứu, không phải hệ thống an toàn được chứng nhận.

## Chuẩn bị dữ liệu và huấn luyện CNN

Kiểm tra nguồn, điều khoản sử dụng, nhãn và cấu trúc dataset trước khi huấn luyện. Dự án không tự động tải dataset. Tải thủ công bộ eye-patch CEW từ trang chính thức, tuân thủ điều khoản nghiên cứu/phi thương mại/không phân phối lại, rồi giải nén vào `data/raw/cew/`. Không đưa dataset hoặc dữ liệu cá nhân vào Git.

```powershell
uv sync --extra train
uv run python scripts/download_dataset.py --archive C:\path\to\CEW-eye-patches.rar
uv run python scripts/prepare_dataset.py --input data/raw/cew/dataset_B_Eye_Images --output data/processed --dataset-name CEW --source-url "https://parnec.nuaa.edu.cn/_upload/tpl/02/db/731/template731/pages/xtan/ClosedEyeDatabases.html" --group-strategy cew-paired-eyes --seed 42
uv run python scripts/train_model.py --manifest data/processed/manifest.csv --checkpoint models/checkpoints/eye_cnn.pt --output outputs/results/eye_cnn-training
```

Nếu có metadata người/phiên, truyền thêm `--groups` với CSV gồm cột `source,group_id`. Nếu không có metadata này, cách nhóm nguồn và phát hiện ảnh trùng không đảm bảo tách độc lập theo người. Lệnh huấn luyện chỉ dùng train/validation và không đọc tập test. Xem [`docs/training.md`](docs/training.md) trước khi đánh giá cuối.

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

| Thành viên | Vai trò | Nhiệm vụ chính |
|---|---|---|
| Huỳnh Vĩnh Lợi | Trưởng nhóm | Định hướng nhóm và câu hỏi nghiên cứu; thống nhất mục tiêu, phạm vi, ưu tiên; phân công và theo dõi tiến độ; điều phối quyết định và rà soát kết quả theo yêu cầu đề tài. |
| Cao Thanh Hùng | Thư ký | Ghi biên bản họp, quyết định và đầu việc; lưu trữ tài liệu, phiên bản báo cáo và hồ sơ hoạt động; nhắc cập nhật tiến độ và kết quả thảo luận. |
| Phạm Nguyễn Phúc Khang | Developer | Quản lý repository và cấu hình dự án; triển khai, tích hợp và xây dựng pipeline/demo; duy trì cấu trúc mã nguồn và hướng dẫn chạy. |
| Dương Công Khoa | Kiểm thử và phụ trách dữ liệu | Kiểm tra yêu cầu, lập và thực hiện kiểm thử, ghi nhận lỗi; theo dõi nguồn và giấy phép dataset, làm sạch/kiểm tra nhãn, chuẩn bị dữ liệu và split hạn chế leakage. |

Các vai trò có thể kiêm nhiệm hoặc điều chỉnh theo khối lượng công việc. Người phụ trách dữ liệu cần ghi rõ nguồn, nhãn, cách tiền xử lý và cách chia tập; dữ liệu tình nguyện viên chỉ được thu thập khi có đồng ý và không đưa vào Git.
## Giấy phép

Dự án được phát hành theo [Giấy phép MIT](LICENSE).
