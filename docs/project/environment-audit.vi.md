# Kiểm toán môi trường

## Runtime và nền tảng

Ghi phiên bản Python, `uv`, hệ điều hành và nền tảng theo kết quả quan sát tại thời điểm kiểm toán. Không lưu định danh máy không cần thiết; lệnh kiểm tra phải có thể chạy lại.

## Dependency và lock

Xác nhận dependency được khai báo, lockfile đồng bộ và trạng thái cài đặt các extra tùy chọn. Phân biệt package đã cài với khả năng thực tế; không suy ra CNN khả dụng chỉ từ khai báo dependency.

## Asset cục bộ và fixture

Kiểm kê model Face Landmarker, checkpoint CNN, dataset và fixture video không cá nhân. Ghi rõ asset thiếu; không tự tải dữ liệu, quay webcam hoặc đưa bí mật vào báo cáo.

## Mốc version control

Ghi nhánh và trạng thái working tree trước thao tác ảnh hưởng lịch sử. Rà soát thay đổi chưa commit; không ghi đè hoặc xóa dữ liệu người dùng.

## Kết luận T-002

Kiểm toán chỉ hoàn tất khi phiên bản, dependency, asset và giới hạn được ghi với nguồn/lệnh tái lập. Đây là quan sát môi trường, không chứng minh hiệu năng ứng dụng.

## Rà soát dependency và bố cục T-003

Đối chiếu kế hoạch đã duyệt với `pyproject.toml`, `src/drowsyalert/`, `tests/` và README. Chỉ đề xuất dependency hoặc thay đổi bố cục khi gắn với yêu cầu cụ thể và có lý do cài đặt/nền tảng; tránh tạo lại module/test sẵn có.

## Cập nhật asset Phase 4

Ghi nhận model/checkpoint cần cho demo và cách tải/bảo quản cục bộ. Asset tải về không được commit; khả năng chạy webcam/âm thanh phải được xác nhận riêng bằng thiết bị thật.
