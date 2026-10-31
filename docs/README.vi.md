# Tài liệu DrowsyAlert

<p><a href="README.md">English</a> | <strong>Tiếng Việt</strong></p>

Thư mục này sắp xếp tài liệu dự án theo mục đích. Đặc tả tính năng, kế hoạch triển khai và danh sách công việc chính thức nằm trong [`specs/001-drowsyalert/`](../specs/001-drowsyalert/).

## Tham khảo (Reference)

- [`reference/de-tai-12-drowsyalert.md`](reference/de-tai-12-drowsyalert.md): mô tả ngắn đề tài 12.
- [`reference/PhieuMoTaDeTai_30DeTai_ThiGiacMayTinh_NCKH.docx`](reference/PhieuMoTaDeTai_30DeTai_ThiGiacMayTinh_NCKH.docx): phiếu mô tả đề tài gốc.

## Dự án

- [`project/architecture.md`](project/architecture.md): cấu trúc mã nguồn, ranh giới và luồng dữ liệu.
- [`project/development-conventions.md`](project/development-conventions.md): quy ước mã, kiểm thử, quyền riêng tư và nhánh.
- [`project/environment-audit.md`](project/environment-audit.md): kiểm tra môi trường và repository có thể tái lập.
- [`project/verification.md`](project/verification.md): bằng chứng kiểm tra tự động và thủ công.
- [`project/phase6-team-handoff.md`](project/phase6-team-handoff.md): quy trình nhóm cho Phase 6.
- [`project/task-tracker/`](project/task-tracker/): trạng thái tiếng Anh/Việt và nhật ký hoạt động.

## Hướng dẫn (Guides)

- [Huấn luyện EyeCNN](guides/training.md) (chưa có bản dịch riêng).
- [Chạy đánh giá A/B/C](guides/evaluation-execution.vi.md) · [Review chú thích](guides/annotation-review.vi.md) · [Kiểm toán dataset video](guides/video-dataset-audit.vi.md).
- [Chính sách âm thanh](guides/audio-policy.vi.md) · [Quy tắc quyết định](guides/decision-policy.vi.md) · [Tính năng nghiên cứu](guides/additional-features.vi.md) · [Hướng dẫn task](guides/task-list-vi.md).

## Nghiên cứu (Research)

- [Thẻ dataset CEW](research/dataset-card.vi.md) · [Thẻ dataset NITYMED](research/nitymed-dataset-card.vi.md).
- [Protocol đánh giá](research/evaluation-protocol.vi.md) · [Metric](research/evaluation-metrics.vi.md) · [Split v1.1](research/evaluation-split-v1.1.vi.md).
- [Quy ước hồ sơ thí nghiệm](research/experiment-records.vi.md) · [Đánh giá pilot](research/pilot-evaluation.vi.md) · [Kết quả validation v1.1](research/validation-evaluation-v1.1.vi.md).
- [Giải thích schema mẫu chú thích](research/annotation-template.vi.md); schema CSV gốc: [`research/annotation-template.csv`](research/annotation-template.csv).

## Tài liệu chưa dịch riêng

Một số tài liệu chuyên sâu vẫn chỉ có bản tiếng Anh: [huấn luyện](guides/training.md), [mô tả đề tài](reference/de-tai-12-drowsyalert.md) (vốn đã viết bằng tiếng Việt), và các tài liệu lưu trữ. Bản dịch của các tài liệu khác được đặt cạnh bản gốc với hậu tố `.vi.md`; thuật ngữ, mã và số liệu được giữ nguyên để đối chiếu.

## Lưu trữ (Archive)

`archive/` chứa tài liệu đã được thay thế, lưu để tra cứu lịch sử và truy vết. Không dùng chúng làm kế hoạch triển khai hiện hành.

Các liên kết ở trên trỏ tới tài liệu tiếng Anh hiện hành; tên tệp và đường dẫn được giữ nguyên để tránh tạo hai nguồn nội dung dễ lệch nhau. Bản tiếng Việt của bảng theo dõi công việc nằm tại [`project/task-tracker/tasks.vi.md`](project/task-tracker/tasks.vi.md). Đặc tả, kế hoạch triển khai và danh sách task chính thức chỉ có một nguồn tại [`specs/001-drowsyalert/`](../specs/001-drowsyalert/).

## Hướng dẫn task bằng tiếng Việt

Đọc [hướng dẫn sử dụng danh sách công việc](guides/task-list-vi.md) trước khi thực hiện task. Tài liệu này giải thích cách đọc trạng thái, phase, gate và quy tắc cập nhật; danh sách chuẩn vẫn là [`specs/001-drowsyalert/tasks.md`](../specs/001-drowsyalert/tasks.md).
