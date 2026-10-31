# Đề tài 12 Phát hiện dấu hiệu buồn ngủ qua webcam

## Đề tài này làm gì

DrowsyAlert quan sát khuôn mặt qua webcam, nhận biết mắt đang mở hay nhắm và theo dõi trạng thái đó theo thời gian. Khi dấu hiệu nhắm mắt kéo dài hoặc các tín hiệu bổ sung cho thấy nguy cơ buồn ngủ, ứng dụng dự kiến hiển thị cảnh báo và phát âm thanh.

Đây là đề tài nghiên cứu khoa học sinh viên, thời gian dự kiến 6–9 tháng. Nguồn yêu cầu là [phiếu mô tả đề tài](PhieuMoTaDeTai_30DeTai_ThiGiacMayTinh_NCKH.docx), mục số 12. Hệ thống là công cụ hỗ trợ tham khảo, không thay thế các biện pháp an toàn giao thông chính thức.

## Tầm nhìn

Xây dựng hệ thống chạy trên webcam và máy tính thông thường, có kết quả đo lường tái lập và giải thích được lý do phát cảnh báo. Hoàn thiện luồng mắt và PERCLOS trước, sau đó bổ sung ngáp và tư thế đầu để trả lời câu hỏi nghiên cứu trong phiếu:

**PERCLOS tính từ landmark 2D có đủ chính xác để phát hiện buồn ngủ, hay cần kết hợp thêm ngáp và tư thế đầu?**

## Một phiên sử dụng dự kiến

1. Người dùng mở ứng dụng và chọn webcam.
2. Hệ thống tìm khuôn mặt, các điểm mốc trên mắt và miệng.
3. Cắt vùng mắt, đưa vào CNN nhẹ để phân loại mở/nhắm.
4. Tổng hợp trạng thái mắt theo thời gian; theo dõi thêm ngáp hoặc tư thế đầu tùy phương pháp.
5. Khi điều kiện cảnh báo kéo dài đủ lâu, hiển thị trạng thái và phát âm thanh.
6. Lưu thông số và kết quả thử nghiệm để đánh giá.

Các bước nhận diện và cảnh báo trên chưa được triển khai trong code hiện tại.

## Thành phần cần xây dựng

| Thành phần | Công việc | Đầu ra |
| --- | --- | --- |
| Video | Đọc webcam/video cùng timestamp | Khung hình và thời gian |
| Detection | Phát hiện khuôn mặt, landmark, cắt mắt bằng mô hình pretrained | Vùng mắt và điểm mốc |
| CNN mắt | Huấn luyện mô hình nhẹ phân loại mắt | Mở/nhắm và độ tin cậy |
| Features | Tính PERCLOS, nhắm mắt liên tục, ngáp, head pose | Tín hiệu theo thời gian |
| Decision | Kết hợp tín hiệu, ngưỡng và thời gian duy trì | Trạng thái và lý do cảnh báo |
| Alert | Hiển thị, phát âm thanh, hạn chế phát lặp | Demo cảnh báo |
| Evaluation | So sánh phương pháp trên cùng dữ liệu | Bảng kết quả và báo cáo |

CNN là mạng nơ-ron tích chập học đặc trưng từ ảnh mắt. Landmark là điểm mốc trên khuôn mặt. EAR là tỉ lệ hình học biểu diễn độ mở của mắt, có thể làm tín hiệu từ landmark để đối chiếu với CNN.

PERCLOS mô tả tỉ lệ thời gian mắt nhắm trong cửa sổ quan sát. Ví dụ, mắt nhắm 12 giây trong 60 giây quan sát hợp lệ tương ứng 20%. Đây là ví dụ minh họa, chưa phải ngưỡng cảnh báo.

Khi triển khai phải thống nhất định nghĩa mắt nhắm, cửa sổ thời gian, cách xử lý chớp mắt và mất khuôn mặt. Dùng timestamp để tính thời gian. Mất quan sát phải là trạng thái riêng, không tự coi là mắt mở hoặc nhắm.

## Dữ liệu

Phiếu đề xuất dữ liệu trạng thái mắt/buồn ngủ công khai trên Kaggle và thử nghiệm với tình nguyện viên có đồng ý. Chưa có URL hoặc phiên bản cụ thể trong phiếu; cần lựa chọn và ghi nguồn trước khi huấn luyện.

- Ảnh mắt mở/nhắm phục vụ huấn luyện và kiểm tra CNN.
- Video có nhãn theo thời gian phục vụ đánh giá cảnh báo.
- Phiên thử nghiệm có kính, ánh sáng yếu và thay đổi góc mặt để phân tích lỗi.

Đề xuất chia train/validation/test theo người hoặc phiên quay khi có thông tin. Tránh các khung hình gần nhau của cùng video xuất hiện ở cả train và test. Chọn ngưỡng trên validation, đánh giá cuối trên test. Ghi nguồn, giấy phép, nhãn và cách chia dữ liệu; lưu thông tin đồng ý khi thu thập tình nguyện viên. Không commit video cá nhân vào Git.

## Ba phương pháp so sánh

| Phương pháp | Tín hiệu | Câu hỏi cần trả lời |
| --- | --- | --- |
| A PERCLOS | Tỉ lệ thời gian mắt nhắm | Baseline hiệu quả đến đâu? |
| B PERCLOS và ngáp | Mắt cùng tín hiệu miệng | Ngáp có cải thiện phát hiện không? |
| C PERCLOS và head pose | Mắt cùng tư thế đầu | Tư thế đầu có cải thiện phát hiện không? |

Dùng cùng tập test, nhãn và cách đo độ trễ. Ghi rõ trạng thái mắt dùng tính PERCLOS đến từ CNN hay landmark/EAR. Đề xuất bổ sung đối chiếu hai cách này để trả lời trực tiếp câu hỏi nghiên cứu; đây là hướng triển khai, chưa có kết quả.

## Đánh giá thành công

Phiếu nêu mục tiêu Accuracy ≥ 0,90 trên tập test cho hệ thống và yêu cầu đo Accuracy phân loại mắt với mục tiêu ≥ 0,90. Phải báo cáo riêng chất lượng phân loại ảnh mắt và hiệu quả cảnh báo trên video.

- Đo Accuracy mắt mở/nhắm và ma trận nhầm lẫn; đề xuất bổ sung Precision, Recall, F1.
- Báo cáo kết quả phát hiện dấu hiệu buồn ngủ của A/B/C trên video có nhãn.
- Đo độ trễ từ thời điểm bắt đầu dấu hiệu được gán nhãn đến lúc phát cảnh báo; ghi rõ cách xác định thời điểm bắt đầu.
- Đề xuất đo cảnh báo giả, bỏ sót, tốc độ xử lý và tỉ lệ mất quan sát.
- Phân tích lỗi theo kính, ánh sáng và góc mặt.

Accuracy ≥ 0,90 là mục tiêu nghiên cứu, chưa phải kết quả đã đạt.

## Phạm vi và sản phẩm

Phạm vi ban đầu: một người trước webcam, xử lý cục bộ, CNN mắt, PERCLOS, demo âm thanh và ba phương pháp thực nghiệm. Sản phẩm bàn giao gồm source code có hướng dẫn, quy trình chuẩn bị dữ liệu, checkpoint và cấu hình, demo webcam, bảng so sánh, ví dụ cảnh báo, báo cáo 35–45 trang và slide.

Ngưỡng thích nghi theo cá nhân và thử nghiệm nhiều tình nguyện viên là hướng phát triển sau baseline. Ứng dụng di động, cloud và tích hợp xe không thuộc phạm vi ban đầu.

## Lộ trình đề xuất

1. Chọn dataset, thống nhất nhãn và cách chia tập.
2. Dựng baseline landmark, EAR và PERCLOS theo timestamp.
3. Huấn luyện CNN mắt, đánh giá và tích hợp suy luận.
4. Hoàn thiện luồng webcam và cảnh báo âm thanh.
5. Bổ sung ngáp, head pose; so sánh A/B/C trên cùng dữ liệu.
6. Phân tích lỗi, đo độ trễ, hoàn thiện báo cáo và hướng dẫn tái lập.

## Hiện trạng

Ứng dụng Python và `pyproject.toml` hiện nằm tại thư mục gốc repository. Mã nguồn có các module nhận diện khuôn mặt, đặc trưng mắt/thời gian, CNN, quyết định và cảnh báo cùng CLI, script và tests. Mô hình đã huấn luyện, tính phù hợp của dataset và kết quả nghiên cứu cần được xác minh riêng trước khi báo cáo.
