# Protocol đánh giá video theo thời gian

**ID:** `drowsyalert-video-eval-v1.1`  
**Trạng thái:** Được duyệt; xem bản tiếng Anh cùng tên nếu cần đối chiếu nguyên văn.

Protocol xác định cách đánh giá cảnh báo buồn ngủ trên video có nhãn theo thời gian. Khóa danh sách clip, split, nhãn tham chiếu, tolerance ghép sự kiện, bin Accuracy, cấu hình và revision mã trước khi chấm test held-out. Tất cả phương pháp A/B/C phải chạy trên cùng clip, nhãn và điều kiện.

## Tách dữ liệu và bảo vệ held-out

Chọn cấu hình/ngưỡng chỉ bằng train/validation. Không xem hoặc dùng kết quả test held-out để lựa chọn ngưỡng, cấu hình, tham số hay phiên bản phương pháp. Sau khi protocol, split, chú thích và cấu hình được khóa, chạy held-out một lần. Báo cáo mọi sai lệch và không thay thế kết quả âm tính bằng lần chạy chọn lọc.

Split hiện tại tách theo clip vì chưa có ánh xạ clip-người tham gia đáng tin cậy. Do đó không tuyên bố độc lập theo đối tượng; công khai nguy cơ một người xuất hiện ở cả hai partition.

## Ground truth và cửa sổ ghép

Reviewer gán khoảng onset/offset theo thời gian media độc lập với đầu ra mô hình. Không dùng EAR, PERCLOS, MAR, pose hoặc cảnh báo hệ thống để tạo nhãn tham chiếu. Các sự kiện được ghép một-một với onset cảnh báo trong cửa sổ tolerance đã khóa: phát hiện sớm tối đa 1 giây, muộn tối đa 2 giây. Cảnh báo ngoài cửa sổ không ghép là báo giả; sự kiện không ghép là bỏ lỡ.

## Metric và báo cáo

Báo cáo metric sự kiện TP/FP/FN, precision, recall, F1; cảnh báo giả trên giờ quan sát hợp lệ; độ trễ onset có dấu; coverage quan sát và thời lượng unknown; cùng Accuracy hệ thống trên bin 1 giây với stride 1 giây và tỷ lệ dương 0,50. UNKNOWN không được xem là NORMAL đúng. Định nghĩa chi tiết nằm trong [metric đánh giá](evaluation-metrics.vi.md).

Trình bày kết quả từng phương pháp và điều kiện, số clip/thời lượng, khoảng tin cậy hoặc giới hạn phù hợp, lỗi/mất quan sát và cấu hình đầy đủ. Tách kết quả phân loại ảnh CEW khỏi đánh giá phát hiện trên video. Không diễn giải metric nghiên cứu thành chứng nhận an toàn.

## Tái lập và giới hạn

Lưu dataset/split ID, hash manifest và nguồn, revision mã, seed, cấu hình đã phân giải, phương pháp, checkpoint nếu dùng, nhãn, giá trị protocol và hồ sơ từng lượt chạy. Artifact riêng tư ở `data/`/`outputs/` không được commit. Dữ liệu NITYMED chưa có ánh xạ người tham gia; mọi kết luận phải nêu rõ split theo clip và nguy cơ rò rỉ người.
