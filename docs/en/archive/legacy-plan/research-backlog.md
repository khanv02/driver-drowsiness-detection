# Backlog mở rộng và NCKH

Các phần dưới đây không chặn bản xây nhanh trong [README.md](README.md). Thực hiện sau khi demo CNN + PERCLOS ước lượng + âm thanh đã chạy, hoặc khi người dùng yêu cầu.

## Mở rộng kỹ thuật

- Phát hiện ngáp và tư thế đầu; hiệu chỉnh định nghĩa và ngưỡng trên dữ liệu validation.
- Ba chế độ PERCLOS, PERCLOS + ngáp, PERCLOS + tư thế đầu.
- Video replay theo timestamp, log CSV và đánh giá độ trễ.
- Kiểm tra đeo kính, ánh sáng yếu, nhiều người và chạy liên tục 30 phút.
- Tối ưu hiệu năng hoặc ngưỡng cá nhân khi có kết quả thực tế.

## Nghiên cứu và viết báo cáo

Giữ lại hướng nghiên cứu của kế hoạch trước; thực hiện khi người dùng yêu cầu review hoặc mở rộng nghiên cứu.

- [ ] Chốt câu hỏi: PERCLOS từ landmark đã đủ tốt hay cần thêm ngáp hoặc tư thế đầu?
- [ ] Hoàn thiện đánh giá CNN trên test giữ riêng, mục tiêu Accuracy ≥ 90%.
- [ ] Thu video khoảng 10–15 tình nguyện viên, hai phiên khoảng 10 phút/người, có đồng ý.
- [ ] Gán nhãn độc lập với dự đoán; kiểm tra chéo tối thiểu 20% video.
- [ ] Chia theo người 40% validation / 60% test; không chia frame cùng người sang hai nhóm.
- [ ] So sánh ba phương pháp với EAR, sau đó với CNN: tổng cộng sáu cấu hình.
- [ ] Chọn ngưỡng trên validation rồi cố định trước test; không tối ưu bằng test.
- [ ] Đánh giá ba luật nghiên cứu riêng với nhánh nhắm mắt liên tục của demo.
- [ ] Báo cáo F1, recall sự kiện, báo động sai/giờ, độ phủ quan sát, độ trễ và FPS.
- [ ] Phân tích theo đeo kính, ánh sáng, người mới và tư thế đầu.
- [ ] Chọn cấu hình bằng validation macro-F1; nếu bằng nhau, ưu tiên ít báo động sai hơn.
- [ ] Thử ngưỡng cá nhân sau khi có kết quả ngưỡng chung.
- [ ] Viết báo cáo 35–45 trang, slide; chỉ viết paper khi dữ liệu và kết quả đủ hỗ trợ đóng góp.

Khung thời gian NCKH 24 tuần trước đây được giữ làm tham chiếu: tuần 1–5 môi trường/baseline; 6–9 CNN; 10–13 tích hợp; 14–19 dữ liệu và thực nghiệm; 20–24 đánh giá cuối và báo cáo. Lịch này không ràng buộc tiến độ xây nhanh hiện tại.

Video mô phỏng chỉ hỗ trợ đánh giá dấu hiệu quan sát được; không dùng để kết luận đã xác nhận trạng thái buồn ngủ thực tế. Giao diện và báo cáo ghi rõ đây là công cụ hỗ trợ tham khảo theo phiếu đề tài.

## Tham khảo kỹ thuật

- [MediaPipe Face Landmarker Python](https://developers.google.com/edge/mediapipe/solutions/vision/face_landmarker/python).
- [Cài đặt MediaPipe Python](https://developers.google.com/edge/mediapipe/solutions/setup_python).
- [PyTorch theo nền tảng và CPU/GPU](https://pytorch.org/get-started/locally/).
- [OpenCV solvePnP](https://docs.opencv.org/4.x/d5/d1f/calib3d_solvePnP.html).
- [NHTSA và định nghĩa PERCLOS](https://www.nhtsa.gov/sites/nhtsa.dot.gov/files/811117.pdf).
