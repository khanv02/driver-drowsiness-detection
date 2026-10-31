# Mẫu schema chú thích

Tệp CSV mẫu đi kèm là schema chuẩn để ghi chú thích sự kiện. Giữ nguyên tên cột và giá trị enum để tương thích công cụ; bản dịch này giải thích ý nghĩa, không thay đổi schema.

- Định danh: clip, dataset, người chú thích và phiên bản schema.
- Khoảng sự kiện: nhãn cùng thời điểm bắt đầu/kết thúc theo thời gian media.
- Nguồn gốc: trạng thái review, phương thức phân xử và độ tin cậy nếu có.
- Nhóm/điều kiện: chỉ điền từ nguồn được xác minh; không suy đoán danh tính từ tên file.

Chỉ dùng nhãn quan sát độc lập với đầu ra mô hình. Bảo quản annotation riêng tư theo quy định dữ liệu; kiểm tra biên thời gian, clip ID, split và giá trị bắt buộc trước khi xuất.
