# Kế hoạch xây nhanh DrowsyAlert

Cập nhật: 13/10/2026.

## 1. Đích đến của bản đầu tiên

Ưu tiên hoàn thành một ứng dụng local có thể chạy và demo:

**Webcam → phát hiện mặt/vùng mắt → CNN mắt mở/nhắm → tỉ lệ nhắm mắt theo thời gian → cảnh báo âm thanh.**

Bản đầu tiên hoàn thành khi người dùng chạy được bằng một lệnh, nhìn thấy trạng thái mắt trên màn hình và nghe cảnh báo khi nhắm mắt kéo dài. CNN là thành phần bắt buộc của bản này; demo EAR chỉ là bước kiểm tra luồng sớm.

Nguồn: [Phiếu mô tả chủ đề 12](../docs/PhieuMoTaDeTai_30DeTai_ThiGiacMayTinh_NCKH.docx).

Chốt phạm vi:

- Windows, CPU, webcam một người; cửa sổ OpenCV.
- Huấn luyện một CNN nhỏ bằng Colab; tải checkpoint về chạy local.
- Tiếp tục làm từ repository root; tận dụng các module và thư mục hiện có.
- Một pipeline, một cách cảnh báo, ít cấu hình.
- Review khi người dùng yêu cầu; không phải điều kiện để chuyển bước.
- Phần NCKH, paper và mở rộng nằm ở [backlog](research-backlog.md).

## 2. Điều chỉnh so với kế hoạch trước

| Điểm làm chậm trong plan cũ | Cách xử lý |
|---|---|
| Sáu mốc, nhiều sản phẩm phụ và review bắt buộc | Ba bước chính; mỗi bước tạo kết quả chạy được |
| Ngáp, head pose, ba chế độ trong điều kiện hoàn thành | Đưa sang phiên bản sau |
| Video replay, log từng frame, nhiều CLI command | Hoãn; bản đầu chỉ cần lệnh webcam và script train |
| Năm trạng thái cảnh báo, nhiều luật kết hợp | Ba trạng thái NORMAL, ALERT, UNKNOWN |
| Kiểm thử điều kiện đa dạng và benchmark đầy đủ | Giữ kiểm tra logic thời gian và smoke test thực tế |
| Đợi dữ liệu tình nguyện viên/thực nghiệm | Dùng dataset công khai để train; không chờ thu dữ liệu |
| Làm đủ kiến trúc trước khi demo | Chỉ tạo module đang dùng, không xây framework |

Ước lượng effort ban đầu: **3–5 ngày làm việc tập trung** nếu môi trường và dữ liệu thuận lợi. Đây là ước lượng để sắp thứ tự, không phải cam kết; cập nhật ngay sau bước 1. Nếu cài dependency hoặc CNN gặp vấn đề, xử lý trực tiếp điểm đó, không mở rộng phạm vi.

## 3. Ba bước triển khai

### Bước 1 — Webcam và cảnh báo bằng EAR

**Mục đích:** kiểm tra nhanh camera, landmark, timestamp và âm thanh trước khi chờ model CNN.

- [ ] Thống nhất Python 3.12, dùng uv; cài dependency cần cho webcam và landmark.
- [ ] Dùng MediaPipe Tasks Face Landmarker với model tải sẵn; xử lý một mặt, VIDEO mode, timestamp tăng dần.
- [ ] OpenCV mở webcam mặc định camera 0, độ phân giải yêu cầu 640 × 480.
- [ ] Tính EAR cho hai mắt, hiển thị vùng mắt, trạng thái và FPS.
- [ ] Dùng monotonic time để đo thời gian hai mắt nhắm liên tục; mặc định cả hai EAR < 0,21.
- [ ] Nhắm liên tục ≥ 2 giây thì phát âm thanh bằng winsound bất đồng bộ; nhắc lại cách nhau ít nhất 5 giây.
- [ ] Mất mặt/vùng mắt chuyển UNKNOWN và reset bộ đếm liên tục; không suy ra mắt mở.
- [ ] Q thoát; giải phóng camera và cửa sổ. Chưa cần thêm phím điều khiển khác.

**Bàn giao:** webcam chạy được, nhắm mắt kéo dài có âm thanh, mở mắt/mất mặt không giữ cảnh báo cũ.

**Ước lượng:** khoảng 1 ngày. Đây là demo kiểm tra luồng, chưa phải bản hoàn thành có CNN.

### Bước 2 — Train CNN và tích hợp vào webcam

**Mục đích:** đưa thành phần CNN của đề tài vào luồng đang chạy, giữ nguyên xử lý thời gian và âm thanh.

- [ ] Dùng [Drowsiness_dataset trên Kaggle](https://www.kaggle.com/datasets/dheerajperumandla/drowsiness-dataset); kiểm tra thư mục nhãn và mẫu ảnh trước khi chuyển đổi.
- [ ] Chỉ dùng ảnh mắt mở/nhắm; không coi nhãn ngáp là nhãn mắt.
- [ ] Loại ảnh lỗi và trùng; chia train/validation/test 70/15/15, seed 42.
- [ ] Nếu có metadata người/phiên, chia theo nhóm; nếu thiếu, nhóm ảnh gần trùng và ghi giới hạn vào kết quả.
- [ ] Với ảnh toàn mặt, dùng landmark cắt mắt; ảnh đã cắt mắt được xử lý trực tiếp sau kiểm tra mẫu.
- [ ] Một hàm tiền xử lý dùng chung: RGB, resize 64 × 64, chuyển tensor về [0, 1]. Chỉ train có augmentation sáng và xoay nhẹ.
- [ ] EyeCNN: ba khối Conv–ReLU–MaxPool với 32/64/128 kênh, Global Average Pooling, Dropout 0,3, đầu ra hai lớp.
- [ ] Train bằng CrossEntropy, Adam 1e-3, batch 64, tối đa 30 epoch; early stopping sau 5 epoch không cải thiện validation F1.
- [ ] Lưu checkpoint tốt nhất theo validation F1, kèm ánh xạ nhãn, cấu trúc model và tiền xử lý.
- [ ] Đo Accuracy, F1 và confusion matrix trên test; tập test không dùng để chọn model/ngưỡng.
- [ ] Tích hợp checkpoint trên CPU; hai mắt cùng có p_closed ≥ 0,5 thì tính là nhắm.
- [ ] EAR chỉ giữ làm lựa chọn debug. Chạy mặc định bằng CNN; thiếu checkpoint báo lỗi rõ ràng, không tự đổi sang EAR.

**Bàn giao:** webcam dùng CNN thật, nhãn mắt cập nhật và âm thanh hoạt động; có checkpoint và kết quả đánh giá.

**Ước lượng:** khoảng 1–2 ngày, phụ thuộc dữ liệu và thời gian train. Có thể khởi động train trên Colab khi phần webcam đang được hoàn thiện.

Mục tiêu Accuracy ≥ 90% được giữ. Nếu chưa đạt, ghi kết quả thực tế và kiểm tra nhãn/crop/lỗi phân loại; không chặn việc tích hợp demo và không tuyên bố đã đạt yêu cầu nghiên cứu.

### Bước 3 — Thêm PERCLOS ước lượng và chốt bản demo

**Mục đích:** hoàn thành luồng theo thời gian của đề tài, kiểm tra các lỗi chính và hướng dẫn chạy.

- [ ] Tính tỉ lệ thời gian hai mắt nhắm trên cửa sổ trượt 60 giây từ kết quả CNN.
- [ ] Chỉ tính khoảng quan sát hợp lệ; dùng timestamp, không đếm frame theo FPS giả định.
- [ ] Nếu khoảng giữa hai mẫu > 0,25 giây hoặc mất mặt/vùng mắt, đánh dấu khoảng đó chưa biết và reset chuỗi nhắm liên tục.
- [ ] Kích hoạt nhánh cửa sổ khi có ít nhất 30 giây quan sát hợp lệ, độ phủ ≥ 80% khoảng cửa sổ đã trôi qua và tỉ lệ nhắm ≥ 0,20.
- [ ] Chờ đủ cửa sổ chỉ áp dụng cho nhánh PERCLOS; nhánh nhắm liên tục ≥ 2 giây vẫn hoạt động ngay từ đầu.
- [ ] Hiển thị trạng thái mắt, tỉ lệ nhắm (hoặc “chưa đủ dữ liệu”), FPS và lý do cảnh báo.
- [ ] Thêm một cấu hình YAML cho camera, checkpoint, model landmark và ngưỡng; không xây hệ thống plugin hoặc cấu hình phân tầng.
- [ ] Kiểm tra chức năng trọng yếu; chạy liên tục ít nhất 10 phút.
- [ ] Viết README ngắn: cài môi trường, tải model, train trên Colab, chạy demo và giới hạn.
- [ ] Giữ dữ liệu, model tải về, checkpoint và đầu ra train ngoài Git; ghi vị trí/cách tải trong README.

**Bàn giao:** bản demo CNN + PERCLOS ước lượng + âm thanh, chạy bằng một lệnh và có hướng dẫn.

**Ước lượng:** khoảng 1–2 ngày.

## 4. Cấu trúc tối thiểu và giao diện

Chỉ tạo các module phục vụ bản đầu:

| Nhóm có sẵn | Module/trách nhiệm cần ngay |
|---|---|
| detection | Wrapper Face Landmarker, crop mắt và EAR dùng debug |
| models | EyeCNN, dataset/tiền xử lý, train và predictor |
| pipeline | Webcam loop, bộ đếm thời gian/cửa sổ, quyết định và âm thanh |
| utils | Đọc YAML và overlay đơn giản |
| tests | Kiểm tra bộ đếm thời gian, dữ liệu thiếu và cooldown |

Giao diện giữa các phần:

- Detector nhận frame BGR và timestamp, trả crop hai mắt, EAR và cờ quan sát hợp lệ.
- Predictor nhận crop mắt, trả xác suất mắt nhắm.
- Bộ xử lý thời gian nhận timestamp và trạng thái CLOSED/OPEN/UNKNOWN, trả thời gian nhắm liên tục, tỉ lệ nhắm và độ phủ cửa sổ.
- Quyết định trả NORMAL/ALERT/UNKNOWN và lý do; phần âm thanh chỉ xử lý phát/nhắc lại.
- Không tạo module rỗng chỉ để đủ cây thư mục.

Lệnh đích, chạy tại repository root:

```powershell
uv run drowsyalert --camera 0 --checkpoint models/checkpoints/eye_cnn.pt
```

Mặc định dùng CNN; thêm --eye-backend ear để kiểm tra khi chưa có checkpoint. Đọc configs/config.yaml mặc định; --camera và --checkpoint ghi đè hai giá trị tương ứng. Train và chuẩn bị dữ liệu dùng script gọi logic trong package, không cần thêm hệ CLI nhiều subcommand.

Các lệnh và module trên là kế hoạch, chưa phải chức năng đã có.

## 5. Kiểm tra đủ dùng và tiêu chí hoàn thành

### Logic cần kiểm tra tự động

- Nhắm liên tục đủ 2 giây kích hoạt; chớp mắt ngắn không kích hoạt.
- Mất mẫu/mất mặt reset chuỗi nhắm, không nối hai đoạn quan sát.
- Tỉ lệ thời gian đúng khi FPS thay đổi; khoảng thiếu không tính thành mắt mở.
- Chưa đủ dữ liệu thì không cảnh báo bằng nhánh cửa sổ.
- Âm thanh không lặp nhanh hơn cooldown.
- Checkpoint tải lại dùng đúng ánh xạ nhãn và tiền xử lý.

### Kiểm tra thủ công

- Camera không mở được, thiếu model, người rời khung và nhắm một mắt.
- Webcam dùng CNN, nhắm/mở mắt thay đổi được trạng thái.
- Âm thanh không làm đứng video; Q thoát và giải phóng camera.
- Chạy liên tục 10 phút và đo FPS hiển thị. Mục tiêu khoảng 15 FPS; chưa cần bộ benchmark.

### Khi nào coi là xong bản xây nhanh?

- [ ] Có checkpoint CNN đã train và kết quả test thực tế.
- [ ] Một lệnh mở webcam và chạy bằng CNN trên CPU.
- [ ] Có tỉ lệ nhắm theo thời gian và cảnh báo nhắm mắt kéo dài.
- [ ] Có NORMAL/ALERT/UNKNOWN; không giữ chuỗi nhắm qua mất mặt.
- [ ] Các kiểm tra trọng yếu ở trên đạt.
- [ ] README giúp chạy lại mà không sửa code.

Không yêu cầu ngáp, head pose, thu tình nguyện viên, sáu cấu hình thực nghiệm hoặc viết paper để hoàn thành bản này. Nếu Accuracy chưa đạt 90%, ghi rõ phần cần cải thiện trước nghiệm thu NCKH.

## 6. Sau khi demo chạy

Chỉ xử lý tiếp khi bản xây nhanh hoàn thành hoặc người dùng yêu cầu:

1. Phát hiện ngáp và head pose bằng landmark.
2. Video replay, log CSV và lựa chọn ba phương pháp.
3. Đánh giá thêm, cải thiện CNN và hiệu chỉnh ngưỡng.
4. Thu dữ liệu tình nguyện viên, nghiên cứu so sánh, báo cáo/paper.

Review có thể diễn ra bất kỳ lúc nào người dùng yêu cầu. Khi review, dùng code, lỗi và kết quả đang có; không bắt buộc làm hồ sơ review riêng cho từng mốc. Chi tiết mở rộng ở [research-backlog.md](research-backlog.md).

Giao diện/README ghi rõ công cụ hỗ trợ tham khảo theo đề tài. Chỉ số từ nhãn mở/nhắm được gọi là PERCLOS ước lượng.
