# Thẻ dataset CEW

## Mục đích và nội dung

CEW (Closed Eyes in the Wild) được dùng cho bài toán phân loại ảnh crop mắt mở/nhắm. Đây là dữ liệu ảnh, không có timeline sự kiện video để đánh giá độ trễ cảnh báo, báo giả theo thời gian hoặc phát hiện buồn ngủ trên video.

## Nguồn và điều khoản

Nguồn, trang chính thức, phiên bản tải, giấy phép/điều khoản và hash archive phải được lưu trong hồ sơ thu nhận. Tuân thủ điều khoản nghiên cứu, phi thương mại và không phân phối lại theo nguồn. Dự án không tự động tải dataset; người dùng tự thu nhận và giữ dữ liệu dưới `data/` bị Git bỏ qua.

## Chuẩn bị và chia tập

Ghi nhận cấu trúc thư mục, quy tắc nhãn, số ảnh và lỗi dữ liệu trong manifest. Loại bản trùng hoặc ảnh lỗi theo quy tắc có thể tái lập. Khi có metadata người/phiên, chia nhóm theo người/phiên để tránh leakage; nếu thiếu metadata, không tuyên bố split độc lập người. Đóng băng train/validation/test trước huấn luyện; chỉ dùng validation chọn cấu hình, test dùng một lần cho đánh giá cuối.

## Kết quả và giới hạn

CEW test được báo cáo cho phân loại ảnh mắt: 728 ảnh, accuracy 0.907967 và macro F1 0.907904. Các số liệu này không phải hiệu suất phát hiện buồn ngủ trên video, bằng chứng an toàn đường bộ hay bảo đảm khái quát sang tài xế thực tế. Không commit ảnh/dataset hoặc dữ liệu cá nhân.
