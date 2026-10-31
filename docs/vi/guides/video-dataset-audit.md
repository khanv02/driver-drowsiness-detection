# Kiểm toán dataset video theo thời gian — Phase 6

**Ngày kiểm toán:** 2026-10-26
**Trạng thái:** NITYMED HDTV720 đã thu nhận và kiểm tra toàn vẹn. Dataset được chọn để chuẩn bị cục bộ Phase 6; chú thích thời gian, nhóm người tham gia, phân split và phê duyệt protocol vẫn bắt buộc trước đánh giá cuối.

Phase 6 cần video khuôn mặt có bằng chứng tham chiếu định vị theo thời gian. CEW của Phase 3 là ảnh mắt, không thể cung cấp onset/offset, độ trễ cảnh báo, báo giả theo thời gian hoặc so sánh A/B/C trên video.

## Kiểm kê cục bộ

- NITYMED HDTV720 chính thức: 126 MP4, 697,049,508 byte, tổng 5,860.677 giây.
- Video giải mã ở 1280×720; 125 clip báo 25 FPS và một clip 24 FPS.
- Manifest và sai khác xem trong [thẻ dataset NITYMED](../research/nitymed-dataset-card.md).
- Corpus chưa có chú thích thời gian và ánh xạ clip-người được xác minh; chưa được duyệt làm corpus held-out.
- Chưa được phép thu video tình nguyện viên. Webcam demo chỉ là bằng chứng demo, không được đổi mục đích thành dữ liệu nghiên cứu held-out.
- Model MediaPipe và checkpoint EyeCNN bị ignore là tài sản triển khai, không phải nhãn tham chiếu.

## Đánh giá ứng viên

| Dataset | Đánh giá và quyết định |
|---|---|
| NITYMED | Clip tập trung sự kiện, phù hợp làm phương án thực tế dự phòng; vẫn cần quyền truy cập, xác minh archive, chú thích thời gian độc lập và duyệt của người hướng dẫn. |
| NTHU-DDD | Có thể có độ phủ hành vi tốt; chỉ cân nhắc nếu lấy từ nhà cung cấp gốc và xác minh được nhãn frame, subject ID, điều khoản. Không dùng mirror chưa xác minh. |
| UTA-RLDD | Có nhãn trạng thái cấp video nhưng không có onset/offset sự kiện cần thiết; cần xác nhận quyền tái sử dụng và chú thích mới. Không phải lựa chọn đầu cho endpoint độ trễ. |
| DROZY | Có video NIR, timestamp và dữ liệu sinh lý; KSS cấp phiên không phải onset sự kiện mặt đã xác minh, miền NIR khác demo RGB. Thỏa thuận hạn chế phân phối, thương mại, nhận dạng và hiển thị ảnh không công bố. |
| Bộ ảnh/crop Kaggle | Bị loại nếu không xác minh được nguồn video gốc, giấy phép, nhóm người/phiên và nhãn thời gian. |

Nguồn chính thức đã rà soát: [NITYMED](https://datasets.esdalab.ece.uop.gr/), [UTA-RLDD](https://sites.google.com/view/utarldd/home), [DROZY](https://www.drozy.ulg.ac.be/) và [hồ sơ ORBi](https://orbi.uliege.be/handle/2268/191620).

## Việc còn lại

1. Lưu bằng chứng đã tuân theo biểu mẫu truy cập và điều khoản NITYMED.
2. Xin ánh xạ người tham gia từ nhà cung cấp nếu có; nếu không, ghi rõ không thể bảo đảm split độc lập người.
3. Chú thích độc lập onset/offset theo media time và review nhãn.
4. Duyệt và khóa protocol trước khi chấm held-out.

Thu video tình nguyện viên vẫn chưa được phép và không cần thiết trong khi đang đánh giá nguồn dữ liệu công khai. Chỉ thu nhận dataset không đồng nghĩa đã được duyệt chấm kết quả cuối.
