# Hồ sơ xác minh

Hồ sơ này tổng hợp bằng chứng kiểm thử tự động, kiểm tra thủ công và các gate nghiệm thu theo phase. Kết quả kiểm thử không chứng minh độ chính xác thực tế hoặc an toàn đường bộ. Nghiệm thu webcam/loa cần phần cứng thật; đánh giá video held-out cần protocol và dữ liệu được duyệt.

## Phase 2 — Landmark và baseline PERCLOS

Đã triển khai luồng landmark, trạng thái mắt `OPEN`/`CLOSED`/`UNKNOWN`, xử lý timestamp, PERCLOS có trọng số thời gian, coverage và trạng thái sẵn sàng. Bằng chứng tự động bao gồm hình học, timestamp, mất quan sát và replay headless. Nghiệm thu G2 dựa trên kiểm tra hành vi và khả năng tái lập; không suy ra hiệu năng ngoài điều kiện đã kiểm thử.

## Phase 3 — Phân loại mắt CNN

CNN được huấn luyện chỉ trên train và chọn bằng validation; test được giữ kín cho đến khi checkpoint/ngưỡng cố định. Trên CEW held-out có 728 ảnh, Accuracy 0.907967 và macro F1 0.907904. Đây là metric phân loại ảnh mắt, không phải metric video buồn ngủ. G3 có bằng chứng tự động và kết quả CEW được ghi trong hướng dẫn huấn luyện.

## Phase 4 — Cảnh báo thời gian thực

Kiểm tra tự động/headless bao phủ pipeline và metadata; smoke test webcam CNN ngắn xác nhận capture/metadata בלבד, không xác nhận GUI hay âm thanh. G4 còn chờ nghiệm thu thiết bị trực tiếp. Checklist phần cứng cần xem chuyển trạng thái, mất/khôi phục quan sát, điều khiển dừng, mute và phát loa; ghi rõ thiết bị và kết quả.

## Phase 5 — Tính năng nghiên cứu bổ sung

Đã kiểm thử sự kiện ngáp theo thời gian, head pose tương đối, bằng chứng riêng cho A/B/C và hồ sơ thí nghiệm JSON/CSV không lưu frame thô mặc định. Nghiệm thu phần mềm G5 đạt theo hồ sơ dự án. Webcam/loa trực tiếp vẫn là kiểm tra phần cứng riêng của G4/T-018.

## Phase 6 — Nền tảng đánh giá thực nghiệm

Protocol v1.1, tài liệu NITYMED và split 38 clip (12 validation, 26 test) được chuẩn bị. Split không trùng clip nhưng chưa có ánh xạ người tham gia, vì vậy không được tuyên bố độc lập theo người. Validation baseline A/B/C có coverage thấp; cấu hình chưa đóng băng và chưa công bố test held-out. Còn cần hoàn tất/review chú thích, lựa chọn cấu hình validation, kiểm tra độc lập test, pilot quy trình và sau đó mới chạy held-out theo protocol.

Test video phải giữ kín trong lúc chọn ngưỡng; kết quả test chỉ chạy sau khi khóa protocol, cấu hình, nhãn và danh tính dữ liệu. Thu hình tình nguyện viên cần phê duyệt và đồng ý; không chuyển dữ liệu demo thành dữ liệu nghiên cứu.

## Phase 7 — Chuẩn bị hồi quy đa nền tảng

Các kiểm tra CI và hồi quy cần chạy theo cấu hình được khóa, ghi revision và bằng chứng có thể tái lập. Không coi cấu hình CI là bằng chứng nghiệm thu webcam/âm thanh thực tế.

## Cách đọc trạng thái

Phân biệt kiểm thử tự động, smoke test, kết quả trên dữ liệu thật và nghiệm thu thủ công. Chỉ đánh dấu gate hoàn tất khi bằng chứng đúng loại đáp ứng tiêu chí; nêu rõ kiểm tra chưa chạy và giới hạn. Tài liệu trạng thái chi tiết/ghi nhận mới nhất nằm trong bản tiếng Anh song song và task chuẩn.
