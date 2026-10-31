# Bàn giao nhóm Phase 6

## Trạng thái hiện tại

Phase 6 tập trung đánh giá video theo thời gian bằng NITYMED. Protocol v1.1 và split clip-disjoint đã được chuẩn bị; ánh xạ người tham gia không có, chú thích/kiểm tra độc lập và lựa chọn cấu hình còn là điều kiện trước khi chấm held-out. CEW chỉ đo phân loại ảnh mắt.

## Bàn giao dữ liệu

Giữ video, manifest chi tiết, worklist, bản nháp và chú thích trong vùng `data/` bị Git bỏ qua. Bàn giao định danh clip, hash, trạng thái review và hướng dẫn truy cập được phép; không gửi dữ liệu thô qua Git. Không suy đoán người tham gia từ tên tệp hoặc thư mục.

## Quy trình review độc lập

Reviewer xác định onset/offset theo media time mà không xem dự đoán mô hình. Kiểm tra nhãn, biên thời gian, điều kiện và metadata; ghi người review, phương thức phân xử và bất đồng. Nếu chỉ có một reviewer, công khai giới hạn. Không đánh dấu reviewed cho đến khi metadata và split được xác nhận.

## Các batch review test

Clip held-out được chia thành batch để điều phối review độc lập, không để lộ đầu ra mô hình. Nhãn test không được dùng chọn ngưỡng; chỉ chạy scoring sau khi protocol và cấu hình được khóa.

## Checklist nghiệm thu T-159

Xác nhận nguồn/quyền truy cập, tính toàn vẹn manifest, trạng thái chú thích, split, hash và quyền riêng tư; đảm bảo không có leakage giữa partition; ghi mọi giới hạn; chuyển giao artifact và chỉ dẫn tái lập. Bàn giao thành công không tự động cho phép chấm held-out nếu gate liên quan chưa hoàn tất.
