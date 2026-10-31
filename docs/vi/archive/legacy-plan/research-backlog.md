# Backlog mở rộng và nghiên cứu khoa học

Các hạng mục này không chặn bản dựng nhanh trong [README](README.md). Chỉ thực hiện sau khi demo CNN + PERCLOS ước lượng + âm thanh chạy, hoặc khi người dùng yêu cầu.

## Mở rộng kỹ thuật

- Phát hiện ngáp và tư thế đầu; hiệu chỉnh định nghĩa/ngưỡng bằng dữ liệu validation.
- Ba chế độ: PERCLOS, PERCLOS + ngáp, PERCLOS + tư thế đầu.
- Phát lại video theo timestamp, ghi CSV và đánh giá độ trễ.
- Kiểm tra kính, ánh sáng yếu, nhiều người và chạy liên tục 30 phút.
- Tối ưu hiệu năng hoặc ngưỡng cá nhân hóa khi có kết quả thực tế.

## Nghiên cứu và báo cáo

Giữ hướng nghiên cứu ban đầu của kế hoạch cũ; chỉ thực hiện khi được yêu cầu review hoặc mở rộng nghiên cứu. Các mục dưới đây là backlog lịch sử, không thay cho protocol hay checklist hiện hành.

- [ ] Chốt câu hỏi: PERCLOS từ landmark đã đủ tốt hay cần thêm ngáp/tư thế đầu?
- [ ] Hoàn tất đánh giá CNN trên test giữ riêng, mục tiêu Accuracy >= 90%.
- [ ] Thu video khoảng 10–15 tình nguyện viên, hai phiên khoảng 10 phút/người, có đồng ý.
- [ ] Gán nhãn độc lập với dự đoán; kiểm tra chéo tối thiểu 20% video.
- [ ] Chia theo người 40% validation / 60% test; không chia frame cùng người sang hai nhóm.
- [ ] So sánh ba phương pháp với EAR, sau đó CNN: tổng cộng sáu cấu hình.
- [ ] Chọn ngưỡng trên validation rồi cố định trước test; không tối ưu bằng test.
- [ ] Đánh giá riêng ba luật nghiên cứu với nhánh nhắm mắt liên tục của demo.
- [ ] Báo cáo F1, recall sự kiện, báo động sai/giờ, coverage quan sát, độ trễ và lỗi theo điều kiện.
- [ ] Viết báo cáo/paper, nêu rõ dữ liệu, giấy phép, split, giới hạn và khả năng tái lập.

Các yêu cầu dữ liệu người tham gia cần được xem xét theo quy định hiện hành và phê duyệt có thẩm quyền; backlog cũ này không cấp quyền thu thập dữ liệu.
